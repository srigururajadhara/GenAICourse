import json
from types import SimpleNamespace

from app.services.chunking import ChunkRecord
from app.services.repository import Repository
from app.services.summarization import SummarizationService


class FakeCompletions:
    def __init__(self, payloads):
        self.payloads = list(payloads)

    def create(self, **kwargs):
        payload = self.payloads.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=payload))])


class FakeClient:
    def __init__(self, payloads):
        self.chat = SimpleNamespace(completions=FakeCompletions(payloads))


def test_summary_preserves_page_citations_and_verifies_claims(tmp_path):
    repo = Repository(tmp_path / "summary.db")
    repo.create_document({
        "document_id": "doc-s", "document_version_id": "doc-s:v1", "workspace_id": "ws-s",
        "file_name": "architecture.pdf", "file_path": str(tmp_path / "a.pdf"), "sha256": "h-s",
    })
    repo.save_chunks("ws-s", "doc-s", [
        ChunkRecord("c-s", "doc-s", 1, 1, "Tech stack", "Next.js is used for the frontend.", 0)
    ])
    client = FakeClient([
        json.dumps({"summary": "The frontend uses Next.js.", "cited_chunk_ids": ["c-s"]}),
        json.dumps({"supported": True, "reason": "Directly supported."}),
    ])
    doc = repo.get_document("ws-s", "doc-s")
    result = SummarizationService(repo=repo, client=client).summarize("ws-s", doc)
    assert result["abstained"] is False
    assert result["citations"][0]["page"] == 1
