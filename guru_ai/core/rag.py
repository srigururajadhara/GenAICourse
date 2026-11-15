from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import OPENAI_MODEL, TOP_K
from core.ingestion import load_vector_store
from core.schemas import QueryRequest, QueryResponse, Citation


SYSTEM_PROMPT = """You are Guru, a careful assistant that explains Indian agricultural government schemes.

NON-NEGOTIABLE RULES:
1. Answer using ONLY the supplied retrieved document excerpts. Do not use prior knowledge to fill gaps.
2. If the documents do not contain enough information, clearly say that the uploaded documents do not specify it. Tell the user what official department or document to verify, without inventing a link.
3. Do not guarantee eligibility, approval, payment, or subsidy. Explain that final eligibility is decided by the relevant government department.
4. Keep important dates, amounts, percentages, land limits, and conditions exactly as written in the sources. Never estimate missing amounts.
5. Add source markers such as [S1] or [S2] beside the claims they support. Do not cite a source that does not support the claim.
6. Use short headings and plain, farmer-friendly language. Explain government terminology when needed.
7. Reply entirely in the requested language. Preserve official scheme names and acronyms where translating them could cause confusion.
8. If the question asks whether a farmer qualifies, compare each stated profile detail only with explicit eligibility rules in the sources. Mark missing profile information as "Needs verification".
9. State clearly when a source appears outdated or gives a particular scheme year. Do not assume it is the currently active version.
"""


def _format_profile(profile: Any) -> str:
    if profile is None:
        return "Not provided"
    return "\n".join(f"- {key}: {value}" for key, value in profile.model_dump(exclude_none=True).items()) or "Not provided"


def ask_guru(request: QueryRequest) -> QueryResponse:
    vector_store = load_vector_store()
    matches = vector_store.similarity_search_with_score(request.question, k=TOP_K)

    # A state-labelled document is preferred for a state-specific farmer profile;
    # All India documents remain eligible evidence.
    if request.farmer_profile and request.farmer_profile.state:
        wanted = request.farmer_profile.state.strip().casefold()
        state_matches = [
            item for item in matches
            if str(item[0].metadata.get("state", "All India")).casefold() in {wanted, "all india", "central"}
        ]
        if state_matches:
            matches = state_matches

    citations: list[Citation] = []
    context_blocks: list[str] = []
    for index, (doc, distance) in enumerate(matches, start=1):
        source_id = f"S{index}"
        page_zero = doc.metadata.get("page")
        page_number = int(page_zero) + 1 if page_zero is not None else None
        source_name = str(doc.metadata.get("source", "Unknown PDF"))
        excerpt = " ".join(doc.page_content.split())[:720]
        state = doc.metadata.get("state")
        category = doc.metadata.get("category")
        citations.append(Citation(
            source=source_name,
            page=page_number,
            state=state,
            category=category,
            excerpt=excerpt,
            source_id=source_id,
        ))
        page_label = f"Page {page_number}" if page_number else "Page not recorded"
        context_blocks.append(
            f"[{source_id}] File: {source_name} | {page_label} | State: {state or 'Not specified'} | Category: {category or 'Not specified'}\n{doc.page_content}"
        )

    if not context_blocks:
        return QueryResponse(
            answer="I could not find matching evidence in the uploaded scheme documents. Try a more specific question or upload the relevant official PDF.",
            citations=[],
            evidence_count=0,
            retrieval_note="No evidence was retrieved.",
            suggested_questions=["Which documents are available in the knowledge base?", "What scheme details are included in the uploaded PDFs?"],
        )

    history_text = "\n".join(
        f"{turn.role.upper()}: {turn.content[:1200]}" for turn in request.chat_history[-8:]
    ) or "No earlier conversation."
    user_prompt = f"""Requested response language: {request.language}

Farmer profile (use only if relevant; do not infer missing information):
{_format_profile(request.farmer_profile)}

Recent conversation:
{history_text}

Retrieved evidence:
{chr(10).join(context_blocks)}

Farmer's question:
{request.question}

Write a helpful, source-grounded answer. Use source markers [S1], [S2], etc. Separate confirmed facts from items that need verification."""

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.1)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])
    answer = response.content if isinstance(response.content, str) else str(response.content)

    return QueryResponse(
        answer=answer,
        citations=citations,
        evidence_count=len(citations),
        retrieval_note="Evidence was retrieved from your uploaded PDFs. Match scores are not a probability of correctness; check the cited page before acting.",
        suggested_questions=[
            "What documents are required to apply?",
            "Which eligibility conditions should I verify?",
            "Summarise the benefits and application steps."
        ],
    )
