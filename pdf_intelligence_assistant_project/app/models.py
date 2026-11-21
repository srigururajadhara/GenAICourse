from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    document_name: str
    page: int
    chunk_id: str
    excerpt: str
    retrieval_sources: list[str] = Field(default_factory=list)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=3000)
    document_id: str
    conversation_history: list[dict[str, str]] = Field(default_factory=list, max_length=12)


class AskResponse(BaseModel):
    answer: str
    abstained: bool
    citations: list[Citation] = Field(default_factory=list)
    retrieval_channels: list[str] = Field(default_factory=list)
    retrieval_warnings: list[str] = Field(default_factory=list)


class SummaryRequest(BaseModel):
    document_id: str
    mode: str = Field(default="executive", pattern="^(executive|detailed|section)$")
    section: str | None = None


class DocumentStatus(BaseModel):
    document_id: str
    file_name: str
    status: str
    vector_status: str
    graph_status: str
    page_count: int | None = None
    warning: str | None = None
    created_at: str
