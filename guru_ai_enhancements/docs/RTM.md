# Guru Enhancements — Requirements Traceability Matrix (RTM)

**Version:** 0.1  
**Status:** Draft — all enhancement requirements awaiting product-owner approval  
**Date:** 15 November 2026

Status values: **Proposed** = documented but not approved; **Approved** = product owner signed off; **Implemented** = code exists; **Verified** = acceptance evidence passed. Requirements in this initial RTM are Proposed only.

| Requirement ID | Requirement summary | Design reference | Planned component (future) | Test ID | Status |
|---|---|---|---|---|---|
| UX-001 | Original Field to Future design system | UI_UX_SPEC §1–3 | `ui/design_tokens` | UX-TC-001 | Proposed |
| UX-002 | Readable text in every dropdown state | UI_UX_SPEC §2, §5 | `ui/select` | UX-TC-002 | Proposed |
| UX-003 | High-contrast dropdown menu and selection states | UI_UX_SPEC §5 | `ui/select` | UX-TC-003 | Proposed |
| UX-004 | Keyboard navigation and visible focus | UI_UX_SPEC §5, §9 | `ui/select`, `ui/components` | UX-TC-004 | Proposed |
| UX-005 | Global text/control contrast and readability | UI_UX_SPEC §4, §9 | `ui/theme`, `ui/components` | UX-TC-005 | Proposed |
| UX-006 | Button state contrast | UI_UX_SPEC §6 | `ui/components` | UX-TC-006 | Proposed |
| UX-007 | Responsive layout | UI_UX_SPEC §7 | `ui/layout` | UX-TC-007 | Proposed |
| UX-008 | Distinct chat/evidence/loading/error/abstention states | UI_UX_SPEC §8 | `ui/chat` | UX-TC-008 | Proposed |
| UX-009 | Consistent page hierarchy and spacing | UI_UX_SPEC §7 | `ui/layout` | UX-TC-009 | Proposed |
| UX-010 | Clear ingestion/API empty, progress and error states | UI_UX_SPEC §7–8 | `ui/feedback` | UX-TC-010 | Proposed |
| UX-011 | Original/licensed assets | UI_UX_SPEC §10 | `ui/assets`, `docs/ASSET_REGISTER.md` | UX-TC-011 | Proposed |
| UX-012 | Baseline user capability regression | FRD §5 | UI/API integration | UX-TC-012 | Proposed |
| RAG-001 | Labelled evaluation set and baseline metrics | ARCHITECTURE §4.5 | `tests/evaluation` | RAG-TC-001 | Proposed |
| RAG-002 | BM25 lexical retrieval | ARCHITECTURE §4.2 | `core/retrieval/lexical` | RAG-TC-002 | Proposed |
| RAG-003 | FAISS semantic retrieval | ARCHITECTURE §4.2 | `core/retrieval/semantic` | RAG-TC-003 | Proposed |
| RAG-004 | RRF fusion and deduplication | ARCHITECTURE §4.2 | `core/retrieval/fusion` | RAG-TC-004 | Proposed |
| RAG-005 | State/category-aware evidence filtering | ARCHITECTURE §4.2 | `core/retrieval/filters` | RAG-TC-005 | Proposed |
| RAG-006 | Cross-encoder reranking | ARCHITECTURE §4.3 | `core/retrieval/reranker` | RAG-TC-006 | Proposed |
| RAG-007 | Contextual query rewriting | ARCHITECTURE §4.1 | `core/query_rewrite` | RAG-TC-007 | Proposed |
| RAG-008 | Preserve original and rewritten query | ARCHITECTURE §4.1, §5 | `core/schemas`, `core/query_rewrite` | RAG-TC-008 | Proposed |
| RAG-009 | Evidence sufficiency and abstention | ARCHITECTURE §4.4 | `core/evidence_gate` | RAG-TC-009 | Proposed |
| RAG-010 | Calibrated threshold; no false probability labels | ARCHITECTURE §4.4 | `core/evidence_gate`, evaluation | RAG-TC-010 | Proposed |
| RAG-011 | Citation support validation | ARCHITECTURE §4.4 | `core/citations` | RAG-TC-011 | Proposed |
| RAG-012 | Metadata traceability across pipeline | ARCHITECTURE §4.2–4.4 | `core/schemas`, retrieval | RAG-TC-012 | Proposed |
| RAG-013 | Repeatable evaluation metrics/report | ARCHITECTURE §4.5 | `tests/evaluation` | RAG-TC-013 | Proposed |
| RAG-014 | Dataset covers core query classes | FRD §6 | `tests/evaluation/dataset` | RAG-TC-014 | Proposed |
| RAG-015 | Preserve six answer languages | FRD §6 | `core/generation`, `ui/chat` | RAG-TC-015 | Proposed |
| RAG-016 | No profile-based invention of scheme facts | FRD §6 | `core/generation`, `core/evidence_gate` | RAG-TC-016 | Proposed |
| RAG-017 | Privacy-aware diagnostics | ARCHITECTURE §4.5 | `core/observability` | RAG-TC-017 | Proposed |
| NFR-001 | Isolate source/data/index from baseline | BASELINE_PROTECTION | project config and paths | NFR-TC-001 | Proposed |
| NFR-002 | Reuse shared `venv312`; no new venv | BASELINE_PROTECTION | setup documentation | NFR-TC-002 | Proposed |
| NFR-003 | WCAG 2.2 AA contrast target | UI_UX_SPEC §9 | UI theme/components | NFR-TC-003 | Proposed |
| NFR-004 | Keyboard accessibility | UI_UX_SPEC §5, §9 | UI components | NFR-TC-004 | Proposed |
| NFR-005 | Benchmark reranker on Intel Mac | ARCHITECTURE §4.3 | benchmark utility | NFR-TC-005 | Proposed |
| NFR-006 | Reproducible evaluation configuration | ARCHITECTURE §4.5 | evaluation runner | NFR-TC-006 | Proposed |
| NFR-007 | Controlled service and pipeline errors | ARCHITECTURE §4.1–4.5 | API/error handling | NFR-TC-007 | Proposed |
| NFR-008 | Do not display raw similarity as probability | FRD §7 | API/UI result model | NFR-TC-008 | Proposed |
| NFR-009 | Preserve non-official decision disclaimer | FRD §7 | generation/UI | NFR-TC-009 | Proposed |
| NFR-010 | Dependencies verified in shared environment | BASELINE_PROTECTION | dependency manifest/CI | NFR-TC-010 | Proposed |

## Traceability rules

1. No requirement is considered approved based only on its presence in this file.
2. After approval, update the requirement status and record the approval date/reference.
3. Every approved requirement must have at least one test ID and an implementation reference once code exists.
4. Mark a requirement **Verified** only after evidence is recorded (test output, screenshot, metric report or review record).
5. Do not silently change requirement meaning; use a change request and preserve ID history.
