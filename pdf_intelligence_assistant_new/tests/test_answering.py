from types import SimpleNamespace

from app.services.answering import AnsweringService
from app.services.chunking import ChunkRecord
from app.services.repository import Repository


class FakeRetriever:
    def retrieve(self, workspace_id, document_id, question):
        return ([{"chunk_id": "chunk-1", "source": "bm25", "retrieval_sources": ["bm25", "faiss"], "rrf_score": 0.04}], [])


class FakeCompletions:
    def __init__(self, payloads):
        self.payloads = list(payloads)

    def create(self, **kwargs):
        content = self.payloads.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class FakeClient:
    def __init__(self, payloads):
        self.chat = SimpleNamespace(completions=FakeCompletions(payloads))


def make_repo(tmp_path):
    repo = Repository(tmp_path / "answer.db")
    repo.create_document({
        "document_id": "doc-1", "document_version_id": "doc-1:v1",
        "workspace_id": "workspace-1", "file_name": "sample.pdf",
        "file_path": str(tmp_path / "sample.pdf"), "sha256": "hash-1",
    })
    repo.save_chunks("workspace-1", "doc-1", [
        ChunkRecord("chunk-1", "doc-1", 2, 2, "Playback", "The Playback Service manages playback state and devices.", 0)
    ])
    return repo, repo.get_document("workspace-1", "doc-1")


def test_answer_requires_valid_citations_and_support_verification(tmp_path):
    repo, doc = make_repo(tmp_path)
    client = FakeClient([
        '{"answer":"The Playback Service manages playback state and devices.","abstain":false,"cited_chunk_ids":["chunk-1"]}',
        '{"supported":true,"reason":"The claims appear in the quoted passage."}',
    ])
    service = AnsweringService(repo=repo, retriever=FakeRetriever(), client=client)
    result = service.ask("workspace-1", doc, "What does the Playback Service manage?")
    assert result["abstained"] is False
    assert result["citations"][0]["page"] == 2
    assert set(result["retrieval_channels"]) == {"bm25", "faiss"}


def test_foreign_or_missing_chunk_cannot_be_cited(tmp_path):
    repo, doc = make_repo(tmp_path)

    class ForeignRetriever:
        def retrieve(self, workspace_id, document_id, question):
            return ([{"chunk_id": "other-workspace-chunk", "source": "neo4j"}], [])

    service = AnsweringService(repo=repo, retriever=ForeignRetriever(), client=FakeClient([]))
    result = service.ask("workspace-1", doc, "What does it do?")
    assert result["abstained"] is True
    assert result["citations"] == []


def test_follow_up_query_is_rewritten_before_hybrid_retrieval(tmp_path):
    from app.core.config import settings

    repo, doc = make_repo(tmp_path)

    class CapturingRetriever:
        def __init__(self):
            self.query = None

        def retrieve(self, workspace_id, document_id, question):
            self.query = question
            return ([{"chunk_id": "chunk-1", "source": "bm25", "retrieval_sources": ["bm25"], "rrf_score": 0.04}], [])

    previous_rewrite = settings.query_rewrite_enabled
    previous_verifier = settings.answer_verifier_enabled
    object.__setattr__(settings, "query_rewrite_enabled", True)
    object.__setattr__(settings, "answer_verifier_enabled", True)
    try:
        retriever = CapturingRetriever()
        client = FakeClient([
            '{"rewritten_query":"What does the Playback Service manage?"}',
            '{"answer":"The Playback Service manages playback state and devices.","abstain":false,"cited_chunk_ids":["chunk-1"]}',
            '{"supported":true,"reason":"Supported by source text."}',
        ])
        service = AnsweringService(repo=repo, retriever=retriever, client=client)
        result = service.ask(
            "workspace-1", doc, "What does it manage?",
            history=[{"role": "user", "content": "Tell me about the Playback Service."}],
        )
        assert retriever.query == "What does the Playback Service manage?"
        assert result["abstained"] is False
    finally:
        object.__setattr__(settings, "query_rewrite_enabled", previous_rewrite)
        object.__setattr__(settings, "answer_verifier_enabled", previous_verifier)
