from __future__ import annotations

import hashlib
import json
import logging
import shutil
import uuid
from pathlib import Path

from app.core.config import settings
from app.services.chunking import ChunkRecord, build_chunks
from app.services.graph_pipeline import GraphPipeline
from app.services.pdf_extractor import extract_pdf
from app.services.repository import Repository, repository

logger = logging.getLogger(__name__)


def workspace_root(workspace_id: str) -> Path:
    # Workspace id comes from a configured API-key mapping; still normalize defensively.
    safe_workspace = uuid.uuid5(uuid.NAMESPACE_DNS, workspace_id).hex
    return settings.storage_root / "workspaces" / safe_workspace


def index_directory(workspace_id: str, document_id: str) -> Path:
    return workspace_root(workspace_id) / "indexes" / document_id


class IngestionService:
    def __init__(self, repo: Repository = repository, vector_pipeline=None, graph_pipeline=None):
        self.repo = repo
        self.vector_pipeline = vector_pipeline
        self.graph_pipeline = graph_pipeline or GraphPipeline()

    def store_upload(self, workspace_id: str, file_name: str, payload: bytes) -> dict:
        if not payload.startswith(b"%PDF-"):
            raise ValueError("The uploaded file does not have a valid PDF signature")
        if len(payload) > settings.max_upload_mb * 1024 * 1024:
            raise ValueError(f"File exceeds the configured {settings.max_upload_mb} MB limit")
        document_id = str(uuid.uuid4())
        checksum = hashlib.sha256(payload).hexdigest()
        version_id = f"{document_id}:{checksum[:12]}"
        destination_dir = workspace_root(workspace_id) / "documents"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{document_id}.pdf"
        destination.write_bytes(payload)
        created = self.repo.create_document(
            {
                "document_id": document_id,
                "document_version_id": version_id,
                "workspace_id": workspace_id,
                "file_name": file_name,
                "file_path": str(destination),
                "sha256": checksum,
            }
        )
        if not created:
            destination.unlink(missing_ok=True)
            raise FileExistsError("This PDF has already been uploaded to this workspace")
        return self.repo.get_document(workspace_id, document_id)

    def ingest(self, workspace_id: str, document_id: str) -> dict:
        document = self.repo.get_document(workspace_id, document_id)
        if not document:
            raise FileNotFoundError("Document was not found in this workspace")
        warnings: list[str] = []
        approved_existing_extraction = document["status"] == "EXTRACTION_APPROVED_PENDING_INDEX"
        try:
            if approved_existing_extraction:
                # Approval resumes from the exact reviewed canonical extraction; do not silently re-parse it.
                saved_chunks = self.repo.get_chunks(workspace_id, document_id)
                if not saved_chunks:
                    raise ValueError("The reviewed extraction is missing its saved passages; retry the upload")
                chunks = [
                    ChunkRecord(
                        chunk_id=row["chunk_id"], document_id=document_id,
                        page_start=row["page_start"], page_end=row["page_end"],
                        section_path=row["section_path"] or "", text=row["text"],
                        chunk_index=row["chunk_index"],
                    )
                    for row in saved_chunks
                ]
                warnings = [document["warning"]] if document.get("warning") else []
                self.repo.update_document(
                    workspace_id, document_id, status="INDEXING_VECTOR", vector_status="RUNNING", graph_status="PENDING"
                )
            else:
                self.repo.update_document(workspace_id, document_id, status="EXTRACTING", warning=None)
                path = Path(document["file_path"])
                blocks, page_count, extraction_warnings = extract_pdf(path, document_id, settings.max_pdf_pages)
                warnings.extend(extraction_warnings)
                chunks = build_chunks(blocks, document_id, settings.max_chunk_chars, settings.chunk_overlap_chars)
                if not chunks:
                    raise ValueError("The PDF produced no indexable text chunks")
                self.repo.save_chunks(workspace_id, document_id, chunks)
                canonical_dir = workspace_root(workspace_id) / "canonical"
                canonical_dir.mkdir(parents=True, exist_ok=True)
                (canonical_dir / f"{document_id}.json").write_text(
                    json.dumps({"blocks": [block.to_dict() for block in blocks], "warnings": extraction_warnings}, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                review_markers = (
                    "low native-text yield", "OCR text extracted", "OCR returned no text",
                    "OCR unavailable or failed", "text extraction failed",
                )
                review_required = any(marker in warning for warning in extraction_warnings for marker in review_markers)
                if review_required:
                    message = "; ".join(extraction_warnings)[:1200]
                    self.repo.update_document(
                        workspace_id, document_id, page_count=page_count,
                        status="EXTRACTION_REVIEW_REQUIRED", vector_status="BLOCKED", graph_status="BLOCKED",
                        warning=message,
                    )
                    self.repo.audit(
                        workspace_id, document_id, "EXTRACTION_REVIEW_REQUIRED",
                        {"warnings": extraction_warnings, "chunk_count": len(chunks)},
                    )
                    return self.repo.get_document(workspace_id, document_id)
                self.repo.update_document(
                    workspace_id, document_id, page_count=page_count, status="INDEXING_VECTOR",
                    vector_status="RUNNING", graph_status="PENDING",
                )
        except Exception as exc:
            message = self._safe_error(exc)
            self.repo.update_document(
                workspace_id, document_id, status="FAILED_RETRYABLE", vector_status="FAILED", graph_status="BLOCKED",
                warning=message,
            )
            self.repo.audit(workspace_id, document_id, "INGESTION_EXTRACTION_FAILED", {"error": message})
            return self.repo.get_document(workspace_id, document_id)

        vector_error = None
        try:
            if self.vector_pipeline is None:
                from app.services.vector_pipeline import VectorLexicalPipeline
                self.vector_pipeline = VectorLexicalPipeline()
            self.vector_pipeline.build(chunks, index_directory(workspace_id, document_id))
            self.repo.update_document(workspace_id, document_id, vector_status="READY", status="INDEXING_GRAPH")
        except Exception as exc:
            vector_error = self._safe_error(exc)
            self.repo.update_document(workspace_id, document_id, vector_status="FAILED")
            logger.error("Vector pipeline failed for document %s (%s)", document_id, type(exc).__name__)

        graph_error = None
        try:
            self.graph_pipeline.build(
                chunks, workspace_id, document_id, document["document_version_id"]
            )
            self.repo.update_document(workspace_id, document_id, graph_status="READY")
        except Exception as exc:
            graph_error = self._safe_error(exc)
            self.repo.update_document(workspace_id, document_id, graph_status="FAILED")
            logger.error("Graph pipeline failed for document %s (%s)", document_id, type(exc).__name__)

        current = self.repo.get_document(workspace_id, document_id)
        if not vector_error and not graph_error:
            status = "READY"
        else:
            status = "FAILED_RETRYABLE"
            warnings.extend([item for item in [vector_error, graph_error] if item])
        self.repo.update_document(
            workspace_id, document_id, status=status,
            warning="; ".join(warnings)[:1200] if warnings else None,
        )
        self.repo.audit(
            workspace_id, document_id, "INGESTION_FINISHED",
            {"status": status, "vector_status": current["vector_status"], "graph_status": current["graph_status"], "warnings": warnings},
        )
        return self.repo.get_document(workspace_id, document_id)

    def approve_extraction(self, workspace_id: str, document_id: str) -> dict:
        document = self.repo.get_document(workspace_id, document_id)
        if not document:
            raise FileNotFoundError("Document was not found in this workspace")
        if document["status"] != "EXTRACTION_REVIEW_REQUIRED":
            raise ValueError("Document is not awaiting extraction review")
        canonical_path = workspace_root(workspace_id) / "canonical" / f"{document_id}.json"
        if not canonical_path.is_file() or not self.repo.get_chunks(workspace_id, document_id):
            raise ValueError("Reviewed extraction data is missing; upload and process the PDF again")
        self.repo.update_document(
            workspace_id, document_id, status="EXTRACTION_APPROVED_PENDING_INDEX",
            vector_status="PENDING", graph_status="PENDING",
        )
        self.repo.audit(workspace_id, document_id, "EXTRACTION_APPROVED_BY_USER", {})
        return self.repo.get_document(workspace_id, document_id)

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        # Keep user-visible errors actionable without exposing provider payloads or secrets.
        if isinstance(exc, (ValueError, FileNotFoundError)):
            return str(exc)[:300]
        if isinstance(exc, RuntimeError) and str(exc):
            return str(exc)[:300]
        return f"{type(exc).__name__}: processing stage failed; inspect protected service logs"

    def delete(self, workspace_id: str, document_id: str) -> None:
        document = self.repo.get_document(workspace_id, document_id)
        if not document:
            raise FileNotFoundError("Document was not found in this workspace")
        # Record intent before cross-store deletion so interrupted cleanup is auditable.
        self.repo.audit(workspace_id, document_id, "DOCUMENT_DELETION_REQUESTED", {})
        # Remove local files first, then graph entities, then metadata.
        path = Path(document["file_path"])
        path.unlink(missing_ok=True)
        for directory in [index_directory(workspace_id, document_id), workspace_root(workspace_id) / "canonical"]:
            if directory.exists() and directory.is_dir():
                if directory.name == "canonical":
                    (directory / f"{document_id}.json").unlink(missing_ok=True)
                else:
                    shutil.rmtree(directory, ignore_errors=True)
        try:
            self.graph_pipeline.delete_document(workspace_id, document_id)
        except Exception:
            # Do not pretend the cross-store deletion completed.
            self.repo.update_document(workspace_id, document_id, status="DELETION_PENDING", warning="Graph deletion failed; retry required")
            self.repo.audit(workspace_id, document_id, "DOCUMENT_DELETION_PENDING", {})
            raise
        self.repo.audit(workspace_id, document_id, "DOCUMENT_DELETED", {})
        self.repo.delete_document_records(workspace_id, document_id)
