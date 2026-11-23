from __future__ import annotations

import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from rank_bm25 import BM25Okapi

from app.core.config import settings
from app.services.chunking import ChunkRecord
from app.services.text_utils import tokenize


class VectorLexicalPipeline:
    def __init__(self, embeddings=None):
        self._embeddings = embeddings

    @property
    def embeddings(self):
        if self._embeddings is None:
            if not settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is required for vector embeddings")
            self._embeddings = OpenAIEmbeddings(
                model=settings.openai_embedding_model, api_key=settings.openai_api_key
            )
        return self._embeddings

    def build(self, chunks: list[ChunkRecord], index_dir: Path) -> None:
        if not chunks:
            raise ValueError("Cannot index a document with no chunks")
        index_dir.mkdir(parents=True, exist_ok=True)
        docs = [
            Document(
                page_content=chunk.text,
                metadata={
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "section_path": chunk.section_path,
                    "chunk_index": chunk.chunk_index,
                },
            )
            for chunk in chunks
        ]
        vector_store = FAISS.from_documents(docs, self.embeddings)
        vector_store.save_local(str(index_dir / "faiss"))
        lexical_payload = [
            {"metadata": doc.metadata, "page_content": doc.page_content, "tokens": tokenize(doc.page_content)}
            for doc in docs
        ]
        (index_dir / "bm25_documents.json").write_text(
            json.dumps(lexical_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest = {
            "chunk_count": len(chunks),
            "embedding_model": settings.openai_embedding_model,
            "index_version": "vector-lexical-v1",
        }
        (index_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def search(self, index_dir: Path, query: str, top_k: int) -> list[dict]:
        faiss_dir = index_dir / "faiss"
        if not faiss_dir.exists():
            return []
        store = FAISS.load_local(
            str(faiss_dir), self.embeddings, allow_dangerous_deserialization=True
        )
        results = store.similarity_search_with_score(query, k=top_k)
        return [
            {
                "chunk_id": doc.metadata["chunk_id"],
                "document_id": doc.metadata["document_id"],
                "page_start": doc.metadata["page_start"],
                "page_end": doc.metadata["page_end"],
                "section_path": doc.metadata.get("section_path", ""),
                "text": doc.page_content,
                "distance": float(score),
                "source": "faiss",
            }
            for doc, score in results
        ]

    @staticmethod
    def bm25_search(index_dir: Path, query: str, top_k: int) -> list[dict]:
        source = index_dir / "bm25_documents.json"
        if not source.exists():
            return []
        rows = json.loads(source.read_text(encoding="utf-8"))
        if not rows:
            return []
        bm25 = BM25Okapi([row["tokens"] for row in rows])
        scores = bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for i in order[:top_k]:
            if scores[i] <= 0:
                continue
            row = rows[i]
            results.append({**row["metadata"], "text": row["page_content"], "score": float(scores[i]), "source": "bm25"})
        return results
