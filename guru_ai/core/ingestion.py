from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from core.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    INDEX_DIR,
    MANIFEST_FILE,
    OPENAI_EMBEDDING_MODEL,
    PDF_DIR,
    ensure_directories,
)


def _read_manifest() -> dict[str, Any]:
    if MANIFEST_FILE.exists():
        try:
            return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"documents": [], "updated_at": None}


def _write_manifest(payload: dict[str, Any]) -> None:
    MANIFEST_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_filename(filename: str) -> str:
    cleaned = Path(filename).name
    cleaned = re.sub(r"[^\w.() -]", "_", cleaned, flags=re.UNICODE).strip(" .")
    return cleaned or "uploaded_document.pdf"


def save_uploaded_pdf(content: bytes, filename: str, state: str, category: str) -> Path:
    ensure_directories()
    safe_name = safe_filename(filename)
    if not safe_name.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")
    destination = PDF_DIR / safe_name
    # Avoid silently overwriting a document with the same name.
    if destination.exists():
        stem, suffix = destination.stem, destination.suffix
        counter = 2
        while (PDF_DIR / f"{stem}_{counter}{suffix}").exists():
            counter += 1
        destination = PDF_DIR / f"{stem}_{counter}{suffix}"
    destination.write_bytes(content)

    manifest = _read_manifest()
    manifest["documents"] = [d for d in manifest.get("documents", []) if d.get("filename") != destination.name]
    manifest["documents"].append({
        "filename": destination.name,
        "state": state,
        "category": category,
        "size_bytes": len(content),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "pages": 0,
        "chunks": 0,
    })
    _write_manifest(manifest)
    return destination


def rebuild_vector_index() -> dict[str, int]:
    """Rebuild FAISS from every PDF in data/pdfs to keep the index reproducible."""
    ensure_directories()
    pdf_paths = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_paths:
        raise ValueError("No PDFs found. Upload at least one official scheme PDF first.")

    manifest = _read_manifest()
    metadata_by_name = {d["filename"]: d for d in manifest.get("documents", [])}
    all_chunks: list[Document] = []
    total_pages = 0
    updated_docs: list[dict[str, Any]] = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    for pdf_path in pdf_paths:
        try:
            pages = PyPDFLoader(str(pdf_path)).load()
        except Exception as exc:  # bad or encrypted files should not break the other PDFs
            updated_docs.append({
                **metadata_by_name.get(pdf_path.name, {}),
                "filename": pdf_path.name,
                "pages": 0,
                "chunks": 0,
                "status": f"Skipped: {str(exc)[:160]}",
            })
            continue

        if not pages:
            continue
        total_pages += len(pages)
        saved_meta = metadata_by_name.get(pdf_path.name, {})
        state = saved_meta.get("state", "All India")
        category = saved_meta.get("category", "Government scheme")
        normalized_pages: list[Document] = []
        for page_doc in pages:
            # PyPDFLoader uses zero-based page metadata; preserve it for exact citations.
            page_doc.metadata.update({
                "source": pdf_path.name,
                "document_id": pdf_path.stem,
                "state": state,
                "category": category,
            })
            normalized_pages.append(page_doc)
        chunks = splitter.split_documents(normalized_pages)
        for chunk in chunks:
            chunk.metadata["source"] = pdf_path.name
            chunk.metadata["state"] = state
            chunk.metadata["category"] = category
        all_chunks.extend(chunks)
        updated_docs.append({
            "filename": pdf_path.name,
            "state": state,
            "category": category,
            "size_bytes": pdf_path.stat().st_size,
            "uploaded_at": saved_meta.get("uploaded_at"),
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "Indexed",
        })

    if not all_chunks:
        raise ValueError("No readable text was extracted. The PDFs may be scanned; OCR support can be added for them.")

    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(all_chunks, embeddings)
    vector_store.save_local(str(INDEX_DIR))

    manifest = {
        "documents": updated_docs,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_pages": total_pages,
        "total_chunks": len(all_chunks),
    }
    _write_manifest(manifest)
    return {"documents": len([d for d in updated_docs if d.get("status") == "Indexed"]), "pages": total_pages, "chunks": len(all_chunks)}


def knowledge_base_stats() -> dict[str, Any]:
    manifest = _read_manifest()
    docs = manifest.get("documents", [])
    indexed = INDEX_DIR.exists() and any(INDEX_DIR.iterdir())
    return {
        "indexed": indexed,
        "documents": len([d for d in docs if d.get("status", "Indexed") == "Indexed"]),
        "pages": manifest.get("total_pages", 0),
        "chunks": manifest.get("total_chunks", 0),
        "updated_at": manifest.get("updated_at"),
        "files": docs,
    }


def load_vector_store() -> FAISS:
    if not INDEX_DIR.exists() or not any(INDEX_DIR.iterdir()):
        raise FileNotFoundError("The knowledge base is empty. Upload PDFs and build the index first.")
    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    # This index is generated and stored locally by this application.
    return FAISS.load_local(
        str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
    )
