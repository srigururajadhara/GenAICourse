from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = Path(os.getenv("DATA_DIR", ROOT_DIR / "data"))
PDF_DIR = DATA_DIR / "pdfs"
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", ROOT_DIR / "storage"))
INDEX_DIR = STORAGE_DIR / "faiss_index"
MANIFEST_FILE = STORAGE_DIR / "manifest.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "160"))
TOP_K = int(os.getenv("TOP_K", "6"))


def ensure_directories() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
