from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core.config import OPENAI_API_KEY, OPENAI_MODEL, ensure_directories
from core.ingestion import knowledge_base_stats, rebuild_vector_index, save_uploaded_pdf
from core.rag import ask_guru
from core.schemas import HealthResponse, QueryRequest, QueryResponse

app = FastAPI(
    title="Guru API",
    description="Source-grounded agricultural government scheme assistant using RAG.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    ensure_directories()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    stats = knowledge_base_stats()
    return HealthResponse(
        status="ok",
        indexed=stats["indexed"],
        documents=stats["documents"],
        chunks=stats["chunks"],
        model=OPENAI_MODEL,
    )


@app.get("/api/v1/knowledge-base")
def knowledge_base() -> dict:
    return knowledge_base_stats()


@app.post("/api/v1/ingest")
async def ingest_pdfs(
    files: list[UploadFile] = File(...),
    state: str = Form("All India"),
    category: str = Form("Government scheme"),
) -> dict:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured in the .env file.")
    saved: list[str] = []
    for uploaded in files:
        if not uploaded.filename or not uploaded.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Please upload PDF files only.")
        content = await uploaded.read()
        if not content:
            continue
        if len(content) > 30 * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"{uploaded.filename} is larger than 30 MB.")
        try:
            path = save_uploaded_pdf(content, uploaded.filename, state, category)
            saved.append(path.name)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not saved:
        raise HTTPException(status_code=400, detail="No non-empty PDF files were uploaded.")
    try:
        stats = rebuild_vector_index()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Index build failed: {exc}") from exc
    return {"message": "Knowledge base rebuilt successfully.", "uploaded": saved, **stats}


@app.post("/api/v1/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured in the .env file.")
    try:
        return ask_guru(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Question processing failed: {exc}") from exc
