from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development").strip().lower()
    app_name: str = os.getenv("APP_NAME", "PDF Intelligence Assistant")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8001"))
    ui_port: int = int(os.getenv("UI_PORT", "8502"))
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8001")
    dev_api_key: str = os.getenv("PDF_ASSISTANT_API_KEY", "local-dev-key-change-before-deployment")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "25"))
    max_pdf_pages: int = int(os.getenv("MAX_PDF_PAGES", "500"))
    max_question_chars: int = int(os.getenv("MAX_QUESTION_CHARS", "3000"))
    max_chunk_chars: int = int(os.getenv("MAX_CHUNK_CHARS", "1600"))
    chunk_overlap_chars: int = int(os.getenv("CHUNK_OVERLAP_CHARS", "200"))
    top_k_vector: int = int(os.getenv("TOP_K_VECTOR", "8"))
    top_k_bm25: int = int(os.getenv("TOP_K_BM25", "8"))
    top_k_graph: int = int(os.getenv("TOP_K_GRAPH", "8"))
    rrf_k: int = int(os.getenv("RRF_K", "60"))
    min_evidence_chunks: int = int(os.getenv("MIN_EVIDENCE_CHUNKS", "1"))
    min_rrf_score: float = float(os.getenv("MIN_RRF_SCORE", "0.0"))
    storage_root: Path = Path(os.getenv("STORAGE_ROOT", "./storage")).resolve()
    sqlite_path: Path = Path(os.getenv("SQLITE_PATH", "./storage/app.db")).resolve()
    ocr_enabled: bool = os.getenv("OCR_ENABLED", "false").lower() == "true"
    ocr_lang: str = os.getenv("OCR_LANG", "eng")
    reranker_enabled: bool = os.getenv("RERANKER_ENABLED", "false").lower() == "true"
    answer_verifier_enabled: bool = os.getenv("ANSWER_VERIFIER_ENABLED", "true").lower() == "true"
    query_rewrite_enabled: bool = os.getenv("QUERY_REWRITE_ENABLED", "true").lower() == "true"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    neo4j_uri: str = os.getenv("NEO4J_URI", "")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    api_keys_json: str = os.getenv("API_KEYS_JSON", "")

    # Authentication configuration
    auth_mode: str = os.getenv("AUTH_MODE", "api_key").strip().lower()
    keycloak_issuer: str = os.getenv("KEYCLOAK_ISSUER", "").strip()
    keycloak_audience: str = os.getenv("KEYCLOAK_AUDIENCE", "").strip()
    keycloak_jwks_url: str = os.getenv("KEYCLOAK_JWKS_URL", "").strip()

    def api_key_map(self) -> dict[str, str]:
        """Return API-key-to-workspace mapping. Secrets are never logged."""
        if self.api_keys_json.strip():
            parsed = json.loads(self.api_keys_json)
            if not isinstance(parsed, dict) or not all(
                isinstance(k, str) and isinstance(v, str) and k and v for k, v in parsed.items()
            ):
                raise ValueError("API_KEYS_JSON must be a JSON object of non-empty key/workspace pairs")
            if any(len(key) < 32 for key in parsed):
                raise ValueError("Every production API key must contain at least 32 characters")
            return parsed
        if self.app_env == "development" and self.dev_api_key:
            return {self.dev_api_key: "local-development"}
        return {}

    def validate(self) -> None:
        if self.app_env == "production":
            if not self.api_key_map():
                raise ValueError("Production requires API_KEYS_JSON with unique, strong API keys")
            if self.dev_api_key == "local-dev-key-change-before-deployment":
                raise ValueError("Replace the development API key before production deployment")
        if self.max_upload_mb < 1 or self.max_pdf_pages < 1:
            raise ValueError("Upload and page limits must be positive")
        if not 0 <= self.chunk_overlap_chars < self.max_chunk_chars:
            raise ValueError("CHUNK_OVERLAP_CHARS must be smaller than MAX_CHUNK_CHARS")


settings = Settings()
