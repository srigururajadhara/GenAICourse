from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from app.services.pdf_extractor import PageBlock


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    document_id: str
    page_start: int
    page_end: int
    section_path: str
    text: str
    chunk_index: int

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "section_path": self.section_path,
            "text": self.text,
            "chunk_index": self.chunk_index,
        }


def _split_text(text: str, max_chars: int, overlap: int) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            boundary = max(text.rfind(". ", start, end), text.rfind("; ", start, end), text.rfind(" ", start, end))
            if boundary > start + int(max_chars * 0.6):
                end = boundary + 1
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


def build_chunks(blocks: list[PageBlock], document_id: str, max_chars: int, overlap: int) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    index = 0
    for block in blocks:
        for piece in _split_text(block.text, max_chars, overlap):
            stable = hashlib.sha256(
                f"{document_id}|{block.page_number}|{index}|{piece}".encode("utf-8")
            ).hexdigest()[:24]
            chunks.append(
                ChunkRecord(
                    chunk_id=stable,
                    document_id=document_id,
                    page_start=block.page_number,
                    page_end=block.page_number,
                    section_path=block.section_path,
                    text=piece,
                    chunk_index=index,
                )
            )
            index += 1
    return chunks
