from __future__ import annotations

import re

from app.core.security import is_suspicious_question


ABSTENTION_TEXT = "I could not find sufficient supporting information in the selected PDF to answer that question."


def validate_question(question: str, maximum: int) -> str:
    cleaned = question.strip()
    if len(cleaned) < 3:
        raise ValueError("Please enter a question containing at least 3 characters")
    if len(cleaned) > maximum:
        raise ValueError(f"Question exceeds the configured {maximum}-character limit")
    if is_suspicious_question(cleaned):
        raise PermissionError("This request is outside the document assistant's permitted scope")
    return cleaned


def validate_graph_candidate(candidate: dict, source_text: str, allowed_entity_types: set[str], allowed_relations: set[str]) -> bool:
    """Require schema membership and an exact supporting quote from the source chunk."""
    quote = str(candidate.get("evidence_quote", "")).strip()
    if not quote or len(quote) > 1200 or quote.casefold() not in source_text.casefold():
        return False
    if candidate.get("kind") == "entity":
        name = str(candidate.get("name", "")).strip()
        entity_type = str(candidate.get("entity_type", "")).upper()
        return bool(len(name) <= 180 and name and name.casefold() in quote.casefold() and entity_type in allowed_entity_types)
    if candidate.get("kind") == "relation":
        subject = str(candidate.get("subject", "")).strip()
        obj = str(candidate.get("object", "")).strip()
        predicate = str(candidate.get("predicate", "")).upper()
        return bool(
            subject and obj and len(subject) <= 180 and len(obj) <= 180 and subject.casefold() in quote.casefold()
            and obj.casefold() in quote.casefold() and predicate in allowed_relations
        )
    return False


def validate_answer_citations(cited_chunk_ids: list[str], allowed_chunk_ids: set[str]) -> bool:
    return (
        isinstance(cited_chunk_ids, list)
        and bool(cited_chunk_ids)
        and all(isinstance(item, str) for item in cited_chunk_ids)
        and set(cited_chunk_ids).issubset(allowed_chunk_ids)
    )


def sanitize_evidence(text: str, maximum: int = 2400) -> str:
    """Bound untrusted document text before model context construction."""
    text = re.sub(r"\x00", "", text)
    return text[:maximum]
