from pathlib import Path

from app.core.config import settings
from app.services.ingestion import IngestionService
from app.services.repository import Repository


class FakeVector:
    def __init__(self):
        self.built = False

    def build(self, chunks, index_dir):
        self.built = True
        Path(index_dir).mkdir(parents=True, exist_ok=True)
        (Path(index_dir) / "fake.index").write_text(str(len(chunks)), encoding="utf-8")


class FakeGraph:
    def __init__(self):
        self.built = False
        self.deleted = False

    def build(self, chunks, workspace_id, document_id, version_id):
        self.built = True
        assert chunks

    def delete_document(self, workspace_id, document_id):
        self.deleted = True


def test_dual_pipeline_status_and_delete(tmp_path):
    old_storage = settings.storage_root
    object.__setattr__(settings, "storage_root", tmp_path / "storage")
    try:
        repo = Repository(tmp_path / "app.db")
        vector = FakeVector()
        graph = FakeGraph()
        service = IngestionService(repo=repo, vector_pipeline=vector, graph_pipeline=graph)
        sample = Path(__file__).resolve().parents[1] / "sample_documents_spotify_web_app_architecture.pdf"
        uploaded = service.store_upload("workspace-test", sample.name, sample.read_bytes())
        processed = service.ingest("workspace-test", uploaded["document_id"])
        assert processed["status"] == "READY"
        assert processed["vector_status"] == "READY"
        assert processed["graph_status"] == "READY"
        assert vector.built and graph.built
        assert repo.get_chunks("workspace-test", uploaded["document_id"])
        service.delete("workspace-test", uploaded["document_id"])
        assert repo.get_document("workspace-test", uploaded["document_id"]) is None
        assert graph.deleted
    finally:
        object.__setattr__(settings, "storage_root", old_storage)


def test_low_text_extraction_requires_explicit_review_before_indexing(tmp_path, monkeypatch):
    import app.services.ingestion as ingestion_module
    from app.services.pdf_extractor import extract_pdf as real_extract_pdf

    old_storage = settings.storage_root
    object.__setattr__(settings, "storage_root", tmp_path / "review-storage")
    try:
        repo = Repository(tmp_path / "review.db")
        vector = FakeVector()
        graph = FakeGraph()
        service = IngestionService(repo=repo, vector_pipeline=vector, graph_pipeline=graph)
        sample = Path(__file__).resolve().parents[1] / "sample_documents_spotify_web_app_architecture.pdf"
        uploaded = service.store_upload("workspace-review", sample.name, sample.read_bytes())
        original_extract = real_extract_pdf

        def extract_with_warning(path, document_id, max_pages):
            blocks, page_count, warnings = original_extract(path, document_id, max_pages)
            return blocks, page_count, [*warnings, "Page 2: low native-text yield; scanned/image-only content may need OCR"]

        monkeypatch.setattr(ingestion_module, "extract_pdf", extract_with_warning)
        review = service.ingest("workspace-review", uploaded["document_id"])
        assert review["status"] == "EXTRACTION_REVIEW_REQUIRED"
        assert review["vector_status"] == "BLOCKED"
        assert review["graph_status"] == "BLOCKED"
        assert not vector.built and not graph.built
        assert repo.get_chunks("workspace-review", uploaded["document_id"])

        approved = service.approve_extraction("workspace-review", uploaded["document_id"])
        assert approved["status"] == "EXTRACTION_APPROVED_PENDING_INDEX"
        processed = service.ingest("workspace-review", uploaded["document_id"])
        assert processed["status"] == "READY"
        assert vector.built and graph.built
    finally:
        object.__setattr__(settings, "storage_root", old_storage)
