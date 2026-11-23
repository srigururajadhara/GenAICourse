from __future__ import annotations

import logging

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import Principal, get_principal, validate_filename
from app.models import AskRequest, AskResponse, SummaryRequest
from app.services.api_state import answering_service, ingestion_service, summarization_service
from app.services.repository import repository
from app.services.guardrails import validate_question

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("pdf_intelligence_assistant")

app = FastAPI(
    title="PDF Intelligence Assistant API",
    version="0.1.0",
    description="PDF-only summarization and evidence-grounded Q&A using vector, lexical and graph retrieval.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8502", "http://127.0.0.1:8502"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
def startup_check() -> None:
    settings.validate()
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    repository.initialize()


def _public_document(row: dict) -> dict:
    return {
        "document_id": row["document_id"],
        "file_name": row["file_name"],
        "status": row["status"],
        "vector_status": row["vector_status"],
        "graph_status": row["graph_status"],
        "page_count": row["page_count"],
        "warning": row["warning"],
        "created_at": row["created_at"],
    }


def _run_ingestion(workspace_id: str, document_id: str) -> None:
    try:
        ingestion_service.ingest(workspace_id, document_id)
    except Exception:
        logger.exception("Unexpected ingestion failure for document %s", document_id)


@app.get("/health/live")
def live():
    return {"status": "alive", "service": "pdf-intelligence-assistant-api", "version": "0.1.0"}


@app.get("/health/ready")
def ready():
    checks = {
        "sqlite": settings.sqlite_path.parent.exists(),
        "storage": settings.storage_root.exists(),
        "openai_configured": bool(settings.openai_api_key),
        "neo4j_configured": bool(settings.neo4j_uri and settings.neo4j_password),
    }
    return {"ready": all(checks.values()), "checks": checks}


@app.get("/api/v1/documents")
def list_documents(principal: Principal = Depends(get_principal)):
    return [_public_document(row) for row in repository.list_documents(principal.workspace_id)]


@app.post("/api/v1/documents", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    principal: Principal = Depends(get_principal),
):
    try:
        file_name = validate_filename(file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if file.content_type not in {"application/pdf", "application/octet-stream", None}:
        raise HTTPException(status_code=415, detail="Only PDF uploads are accepted")
    payload = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    try:
        document = ingestion_service.store_upload(principal.workspace_id, file_name, payload)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await file.close()
    background_tasks.add_task(_run_ingestion, principal.workspace_id, document["document_id"])
    return _public_document(document)


@app.get("/api/v1/documents/{document_id}")
def get_document(document_id: str, principal: Principal = Depends(get_principal)):
    row = repository.get_document(principal.workspace_id, document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    return _public_document(row)


@app.post("/api/v1/documents/{document_id}/retry", status_code=status.HTTP_202_ACCEPTED)
def retry_ingestion(document_id: str, background_tasks: BackgroundTasks, principal: Principal = Depends(get_principal)):
    row = repository.get_document(principal.workspace_id, document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    if row["status"] not in {"FAILED_RETRYABLE", "UPLOADED"}:
        raise HTTPException(status_code=409, detail=f"Document cannot be retried from status {row['status']}")
    repository.update_document(
        principal.workspace_id, document_id, status="UPLOADED", vector_status="PENDING", graph_status="PENDING", warning=None
    )
    background_tasks.add_task(_run_ingestion, principal.workspace_id, document_id)
    return {"document_id": document_id, "status": "RETRY_QUEUED"}


@app.post("/api/v1/documents/{document_id}/approve-extraction", status_code=status.HTTP_202_ACCEPTED)
def approve_extraction(
    document_id: str, background_tasks: BackgroundTasks, principal: Principal = Depends(get_principal)
):
    try:
        document = ingestion_service.approve_extraction(principal.workspace_id, document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    background_tasks.add_task(_run_ingestion, principal.workspace_id, document_id)
    return {"document_id": document["document_id"], "status": "APPROVED_AND_INDEXING"}


@app.delete("/api/v1/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, principal: Principal = Depends(get_principal)):
    try:
        ingestion_service.delete(principal.workspace_id, document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    except Exception as exc:
        logger.exception("Document deletion is incomplete: %s", document_id)
        raise HTTPException(status_code=503, detail="Deletion is pending; graph cleanup must be retried") from exc


@app.post("/api/v1/ask", response_model=AskResponse)
def ask(request: AskRequest, principal: Principal = Depends(get_principal)):
    try:
        question = validate_question(request.question, settings.max_question_chars)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    document = repository.get_document(principal.workspace_id, request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document["status"] != "READY":
        raise HTTPException(status_code=409, detail="Both vector and graph pipelines must complete before Q&A is enabled")
    try:
        result = answering_service.ask(
            principal.workspace_id, document, question, request.conversation_history
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Q&A failed")
        raise HTTPException(status_code=503, detail="The answer service is temporarily unavailable") from exc
    return result


@app.post("/api/v1/summaries")
def summarize(request: SummaryRequest, principal: Principal = Depends(get_principal)):
    document = repository.get_document(principal.workspace_id, request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document["status"] != "READY":
        raise HTTPException(status_code=409, detail="Both vector and graph pipelines must complete before summaries are enabled")
    if request.mode == "section" and not request.section:
        raise HTTPException(status_code=422, detail="A section heading is required for section summaries")
    try:
        return summarization_service.summarize(
            principal.workspace_id, document, request.mode, request.section
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Summary generation failed")
        raise HTTPException(status_code=503, detail="The summary service is temporarily unavailable") from exc


@app.get("/api/v1/documents/{document_id}/chunks")
def list_chunks(document_id: str, principal: Principal = Depends(get_principal)):
    document = repository.get_document(principal.workspace_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return [
        {"chunk_id": row["chunk_id"], "page": row["page_start"], "section": row["section_path"], "text": row["text"]}
        for row in repository.get_chunks(principal.workspace_id, document_id)
    ]
