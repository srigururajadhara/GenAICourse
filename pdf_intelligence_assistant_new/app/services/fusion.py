from __future__ import annotations

from collections import defaultdict


def reciprocal_rank_fusion(result_lists: list[list[dict]], k: int = 60, top_k: int = 10) -> list[dict]:
    """Combine ranked retrieval channels using RRF, keyed by canonical chunk_id."""
    scores: dict[str, float] = defaultdict(float)
    records: dict[str, dict] = {}
    channels: dict[str, set[str]] = defaultdict(set)
    for result_list in result_lists:
        for rank, item in enumerate(result_list, start=1):
            chunk_id = item.get("chunk_id")
            if not chunk_id:
                continue
            scores[chunk_id] += 1.0 / (k + rank)
            records.setdefault(chunk_id, item.copy())
            channels[chunk_id].add(str(item.get("source", "unknown")))
    ranked = []
    for chunk_id, score in scores.items():
        item = records[chunk_id]
        item["rrf_score"] = score
        item["retrieval_sources"] = sorted(channels[chunk_id])
        ranked.append(item)
    return sorted(ranked, key=lambda item: item["rrf_score"], reverse=True)[:top_k]
