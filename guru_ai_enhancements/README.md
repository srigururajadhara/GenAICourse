# Guru Enhancements — Requirements & Design Pack

**Product:** Guru — Agricultural Government Scheme Assistant  
**Project:** `guru_ai_enhancements`  
**Requirements pack:** v0.1  
**Date:** 15 November 2026  
**Status:** Draft for product-owner review — **no implementation authorised yet**

## 1. Purpose

This separate project is the controlled enhancement track for the existing Guru application. It captures the agreed user-experience direction and the proposed Advanced RAG improvements before any code is written.

## 2. Baseline protection

- The existing `GenAICourse/guru_ai` is the protected, working baseline. Do not edit, rename, delete, overwrite, or import code from it as a write target.
- All future enhancement implementation belongs in `GenAICourse/guru_ai_enhancements`.
- The existing shared `GenAICourse/venv312` may be activated for this project. Do **not** create another virtual environment unless the product owner explicitly changes this decision.
- The enhanced project must have its own `.env`, PDF folder, vector index, manifest, logs and test fixtures. Never point it at the baseline project's `data/` or `storage/` directories.
- This package intentionally contains documentation and empty project folders only. There is no `app.py`, API code, retrieval code or dependency file yet.

See [Baseline Protection](docs/BASELINE_PROTECTION.md).

## 3. What we are proposing

### UX direction — accepted as the visual direction; detailed criteria need sign-off

**Field to Future**: an original Guru design language inspired by India's agricultural landscape. The goal is a distinct product identity, not a recoloured copy of a generic dashboard or another product. The palette, layout, component rules and interaction requirements are in [UI/UX Specification](docs/UI_UX_SPEC.md).

The reported dropdown issue is explicitly captured: the open Irrigation menu showed dark green option text on a near-black background, making choices unreadable. Every dropdown, including the open option list, must have readable foreground/background contrast.

### Advanced RAG — proposed Phase 1 scope

1. Establish an evaluated baseline using a labelled agricultural-scheme question set.
2. Add contextual query rewriting for follow-up questions.
3. Add hybrid lexical + semantic retrieval (BM25 + FAISS) with rank fusion.
4. Add cross-encoder reranking of retrieved candidates.
5. Add an evidence-quality / abstention gate so Guru declines to assert answers when support is insufficient.
6. Evaluate retrieval, answer grounding, citation quality, multilingual behaviour, latency and cost.

These are proposals in this pack, not permission to implement them. See [FRD](docs/FRD.md), [Architecture](docs/ARCHITECTURE.md), [RTM](docs/RTM.md), and [Backlog](docs/FEATURE_BACKLOG.md).

## 4. Current baseline — source-reviewed summary

The baseline source snapshot reviewed for this requirements pack uses:

- Streamlit for the farmer-facing dashboard and chat.
- FastAPI endpoints: `GET /health`, `GET /api/v1/knowledge-base`, `POST /api/v1/ingest`, and `POST /api/v1/query`.
- `PyPDFLoader` for text-based PDF page extraction.
- `RecursiveCharacterTextSplitter` for chunking.
- OpenAI embeddings and a local FAISS index.
- Semantic `similarity_search_with_score` retrieval with configured `TOP_K`.
- GPT-4o-mini for source-grounded answer generation.
- Recent chat turns included in the answer-generation prompt, while retrieval currently searches the latest question as written.
- State preference filtering applied after the initial semantic top-K result set.
- Citation payloads containing source filename, page, state, category and excerpt.
- Eligibility guidance is LLM-assisted profile/document comparison, not a deterministic government-rule engine.

The baseline README and source snapshot are the basis for this summary. The currently running local app may include the contrast-refresh `app.py` that the user copied into their working folder. The precise local working tree has not been directly inspected in this session; the user-reported working state is therefore treated as the operational baseline.

## 5. Pack contents

| File | Purpose |
|---|---|
| `docs/PROJECT_CHARTER.md` | Goals, scope, roles, constraints and success measures |
| `docs/FRD.md` | Functional and non-functional requirements |
| `docs/UI_UX_SPEC.md` | Field to Future visual and interaction requirements |
| `docs/ARCHITECTURE.md` | Baseline architecture and proposed target architecture |
| `docs/RTM.md` | Requirement-to-design-to-test traceability |
| `docs/TEST_PLAN.md` | Proposed test strategy and acceptance scenarios |
| `docs/FEATURE_BACKLOG.md` | Prioritised enhancement backlog and phase boundaries |
| `docs/BASELINE_PROTECTION.md` | Rules that keep the working `guru_ai` untouched |
| `docs/APPROVAL_WORKFLOW.md` | Requirement review and implementation authorisation process |
| `docs/APPROVAL_CHECKLIST.md` | Sign-off checklist for the product owner |
| `docs/CHANGE_REQUEST_TEMPLATE.md` | Template for future scope changes |
| `docs/DECISION_LOG.md` | Recorded decisions and open decisions |

## 6. Review status

- The product owner has agreed to keep the original `guru_ai` project untouched and use a separate enhancement folder.
- The product owner has accepted the **Field to Future** visual direction in principle.
- The dropdown readability defect has been confirmed from a screenshot.
- The full detailed FRD, architecture, test scenarios and phase acceptance criteria in this pack are **draft and require explicit approval**.
- No implementation changes are included in this package.

## 7. Next step

Review `docs/APPROVAL_CHECKLIST.md`. After any requested revisions, the product owner can explicitly approve the requirements. Only then should implementation planning and code changes begin in this separate project.
