from app.services.fusion import reciprocal_rank_fusion


def test_rrf_rewards_items_ranked_by_multiple_channels():
    results = reciprocal_rank_fusion(
        [
            [{"chunk_id": "a", "source": "faiss"}, {"chunk_id": "b", "source": "faiss"}],
            [{"chunk_id": "b", "source": "bm25"}, {"chunk_id": "a", "source": "bm25"}],
            [{"chunk_id": "b", "source": "neo4j"}],
        ],
        k=60,
        top_k=5,
    )
    assert results[0]["chunk_id"] == "b"
    assert set(results[0]["retrieval_sources"]) == {"faiss", "bm25", "neo4j"}
    assert len({item["chunk_id"] for item in results}) == len(results)


def test_rrf_ignores_results_without_stable_chunk_ids():
    results = reciprocal_rank_fusion([[{"text": "not indexable"}, {"chunk_id": "good", "source": "bm25"}]])
    assert [item["chunk_id"] for item in results] == ["good"]
