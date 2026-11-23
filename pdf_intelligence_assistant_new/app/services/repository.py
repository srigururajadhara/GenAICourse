from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.services.chunking import ChunkRecord


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.sqlite_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        connection = sqlite3.connect(self.db_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    document_version_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    status TEXT NOT NULL,
                    vector_status TEXT NOT NULL,
                    graph_status TEXT NOT NULL,
                    page_count INTEGER,
                    warning TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(workspace_id, sha256)
                );
                CREATE INDEX IF NOT EXISTS idx_documents_workspace ON documents(workspace_id, created_at);
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    page_start INTEGER NOT NULL,
                    page_end INTEGER NOT NULL,
                    section_path TEXT,
                    text TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(workspace_id, document_id);
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace_id TEXT NOT NULL,
                    document_id TEXT,
                    event_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    details_json TEXT NOT NULL
                );
                """
            )

    def create_document(self, document: dict) -> bool:
        with self.connect() as con:
            duplicate = con.execute(
                "SELECT document_id FROM documents WHERE workspace_id=? AND sha256=?",
                (document["workspace_id"], document["sha256"]),
            ).fetchone()
            if duplicate:
                return False
            now = utc_now()
            con.execute(
                """INSERT INTO documents
                (document_id, document_version_id, workspace_id, file_name, file_path, sha256,
                 status, vector_status, graph_status, page_count, warning, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'UPLOADED', 'PENDING', 'PENDING', NULL, NULL, ?, ?)""",
                (
                    document["document_id"], document["document_version_id"], document["workspace_id"],
                    document["file_name"], document["file_path"], document["sha256"], now, now,
                ),
            )
            con.execute(
                "INSERT INTO audit_events (workspace_id, document_id, event_type, created_at, details_json) VALUES (?, ?, ?, ?, ?)",
                (document["workspace_id"], document["document_id"], "DOCUMENT_UPLOADED", now, "{}"),
            )
            return True

    def get_document(self, workspace_id: str, document_id: str) -> dict | None:
        with self.connect() as con:
            row = con.execute(
                "SELECT * FROM documents WHERE workspace_id=? AND document_id=?",
                (workspace_id, document_id),
            ).fetchone()
            return dict(row) if row else None

    def list_documents(self, workspace_id: str) -> list[dict]:
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM documents WHERE workspace_id=? ORDER BY created_at DESC",
                (workspace_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def update_document(self, workspace_id: str, document_id: str, **fields) -> None:
        allowed = {"status", "vector_status", "graph_status", "page_count", "warning"}
        changes = {key: value for key, value in fields.items() if key in allowed}
        if not changes:
            return
        changes["updated_at"] = utc_now()
        assignments = ", ".join(f"{key}=?" for key in changes)
        values = list(changes.values()) + [workspace_id, document_id]
        with self.connect() as con:
            con.execute(
                f"UPDATE documents SET {assignments} WHERE workspace_id=? AND document_id=?", values
            )

    def save_chunks(self, workspace_id: str, document_id: str, chunks: list[ChunkRecord]) -> None:
        with self.connect() as con:
            con.execute("DELETE FROM chunks WHERE workspace_id=? AND document_id=?", (workspace_id, document_id))
            con.executemany(
                """INSERT INTO chunks
                (chunk_id, workspace_id, document_id, page_start, page_end, section_path, text, chunk_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (c.chunk_id, workspace_id, document_id, c.page_start, c.page_end,
                     c.section_path, c.text, c.chunk_index)
                    for c in chunks
                ],
            )

    def get_chunks(self, workspace_id: str, document_id: str) -> list[dict]:
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM chunks WHERE workspace_id=? AND document_id=? ORDER BY chunk_index",
                (workspace_id, document_id),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_chunks_by_ids(self, workspace_id: str, document_id: str, chunk_ids: list[str]) -> list[dict]:
        if not chunk_ids:
            return []
        placeholders = ",".join("?" for _ in chunk_ids)
        with self.connect() as con:
            rows = con.execute(
                f"SELECT * FROM chunks WHERE workspace_id=? AND document_id=? AND chunk_id IN ({placeholders})",
                [workspace_id, document_id, *chunk_ids],
            ).fetchall()
            by_id = {row["chunk_id"]: dict(row) for row in rows}
            return [by_id[item] for item in chunk_ids if item in by_id]

    def audit(self, workspace_id: str, document_id: str | None, event_type: str, details: dict) -> None:
        with self.connect() as con:
            con.execute(
                "INSERT INTO audit_events (workspace_id, document_id, event_type, created_at, details_json) VALUES (?, ?, ?, ?, ?)",
                (workspace_id, document_id, event_type, utc_now(), json.dumps(details, ensure_ascii=False)),
            )

    def delete_document_records(self, workspace_id: str, document_id: str) -> None:
        with self.connect() as con:
            con.execute("DELETE FROM documents WHERE workspace_id=? AND document_id=?", (workspace_id, document_id))


repository = Repository()
