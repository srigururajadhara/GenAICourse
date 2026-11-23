from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.core.config import settings
from app.services.fusion import reciprocal_rank_fusion
from app.services.graph_pipeline import GraphPipeline
from app.services.ingestion import index_directory
from app.services.vector_pipeline import VectorLexicalPipeline



class HybridRetriever:
    def __init__(self, vector_pipeline=None, graph_pipeline=None):
        self.vector = vector_pipeline or VectorLexicalPipeline()
        self.graph = graph_pipeline or GraphPipeline()

    def retrieve(self, workspace_id: str, document_id: str, query: str) -> tuple[list[dict], list[str]]:
        directory = index_directory(workspace_id, document_id)
        tasks = {
            "faiss": lambda: self.vector.search(directory, query, settings.top_k_vector),
            "bm25": lambda: self.vector.bm25_search(directory, query, settings.top_k_bm25),
            "neo4j": lambda: self.graph.search(workspace_id, document_id, query, settings.top_k_graph),
        }
        results: dict[str, list[dict]] = {}
        errors: list[str] = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fn): name for name, fn in tasks.items()}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result()
                except Exception as exc:
                    # A retrieval channel failure is made observable; other validated channels can still contribute.
                    errors.append(f"{name}: {type(exc).__name__}")
                    results[name] = []
        fused = reciprocal_rank_fusion(
            [results.get("faiss", []), results.get("bm25", []), results.get("neo4j", [])],
            k=settings.rrf_k,
            top_k=max(settings.top_k_vector, settings.top_k_bm25, settings.top_k_graph),
        )
        if settings.min_rrf_score > 0:
            fused = [item for item in fused if item["rrf_score"] >= settings.min_rrf_score]
        return fused, errors
