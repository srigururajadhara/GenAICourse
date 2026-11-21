from app.services.metrics import abstention_accuracy, citation_page_accuracy, recall_at_k, reciprocal_rank


def test_retrieval_metrics():
    assert recall_at_k(["a", "b", "c"], {"b", "z"}, k=3) == 0.5
    assert reciprocal_rank(["x", "b", "a"], {"b"}) == 0.5


def test_citation_and_abstention_metrics():
    assert citation_page_accuracy([1, 2], {2}) == 0.5
    assert abstention_accuracy([False, True, True], [False, True, False]) == 2 / 3
