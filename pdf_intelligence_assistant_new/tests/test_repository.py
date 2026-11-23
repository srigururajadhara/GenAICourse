from app.services.repository import Repository


def document(doc_id: str, workspace: str, sha: str):
    return {
        "document_id": doc_id,
        "document_version_id": f"{doc_id}:v1",
        "workspace_id": workspace,
        "file_name": f"{doc_id}.pdf",
        "file_path": f"/tmp/{doc_id}.pdf",
        "sha256": sha,
    }


def test_repository_enforces_workspace_scoping(tmp_path):
    repo = Repository(tmp_path / "test.db")
    assert repo.create_document(document("doc-a", "workspace-a", "hash-a"))
    assert repo.get_document("workspace-a", "doc-a") is not None
    assert repo.get_document("workspace-b", "doc-a") is None
    assert repo.list_documents("workspace-b") == []


def test_duplicate_hash_is_rejected_within_workspace(tmp_path):
    repo = Repository(tmp_path / "test.db")
    assert repo.create_document(document("doc-a", "workspace-a", "same-hash"))
    assert not repo.create_document(document("doc-b", "workspace-a", "same-hash"))
    # The same bytes can exist in a different workspace, without cross-workspace discovery.
    assert repo.create_document(document("doc-c", "workspace-b", "same-hash"))
