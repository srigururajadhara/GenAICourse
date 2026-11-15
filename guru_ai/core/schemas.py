from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=8000)


class FarmerProfile(BaseModel):
    state: str | None = None
    district: str | None = None
    farmer_type: str | None = None
    land_size_acres: float | None = Field(default=None, ge=0)
    social_category: str | None = None
    crop: str | None = None
    irrigation: str | None = None


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    language: str = "English"
    farmer_profile: FarmerProfile | None = None
    chat_history: list[ChatTurn] = Field(default_factory=list, max_length=12)


class Citation(BaseModel):
    source: str
    page: int | None = None
    state: str | None = None
    category: str | None = None
    excerpt: str
    source_id: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    evidence_count: int
    retrieval_note: str
    suggested_questions: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    indexed: bool
    documents: int
    chunks: int
    model: str
