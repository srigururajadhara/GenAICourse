from __future__ import annotations


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int = 5) -> float:
    if not relevant_ids:
        return 1.0
    return len(set(retrieved_ids[:k]) & relevant_ids) / len(relevant_ids)


def reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    for rank, item in enumerate(retrieved_ids, start=1):
        if item in relevant_ids:
            return 1.0 / rank
    return 0.0


def citation_page_accuracy(cited_pages: list[int], expected_pages: set[int]) -> float:
    if not expected_pages:
        return 1.0 if not cited_pages else 0.0
    if not cited_pages:
        return 0.0
    return len(set(cited_pages) & expected_pages) / len(set(cited_pages))


def abstention_accuracy(expected_unanswerable: list[bool], actual_abstained: list[bool]) -> float:
    if len(expected_unanswerable) != len(actual_abstained) or not expected_unanswerable:
        raise ValueError("Expected and actual abstention arrays must be non-empty and equal length")
    return sum(expected == actual for expected, actual in zip(expected_unanswerable, actual_abstained)) / len(expected_unanswerable)
