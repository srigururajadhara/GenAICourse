# Guru Enhancements — Prioritised Backlog

**Version:** 0.1  
**Status:** Proposed only; no implementation authorised  
**Date:** 15 November 2026

| Priority | ID | Feature | Outcome | Dependency / note |
|---|---|---|---|---|
| P0 | UX-01 | Field to Future UI system | Original Guru identity and consistent visual components | UX requirements approval |
| P0 | UX-02 | Dropdown visibility and accessibility | Readable open menus, clear selected/unselected/focus states | Must be tested in Chrome on macOS |
| P0 | UX-03 | Global contrast/readability | No unreadable text across buttons, tabs, inputs, chat, alerts or captions | Contrast/accessibility checks |
| P0 | BASE-01 | Baseline protection and project isolation | Original `guru_ai` untouched; separate data/index/env config | Enforce path checks |
| P1 | EVAL-01 | Evaluation dataset and baseline report | Know current quality before changing retrieval | Requires human-labelled evidence |
| P1 | RAG-01 | BM25 lexical retrieval | Improve exact-name, acronym, number and section retrieval | Chunk IDs and metadata |
| P1 | RAG-02 | FAISS semantic retrieval adapter | Preserve semantic retrieval and expose common candidate schema | Existing semantic approach is baseline |
| P1 | RAG-03 | RRF hybrid fusion | Combine lexical and semantic rankings | Deduplication/stable IDs |
| P1 | RAG-04 | Context-aware query rewriting | Improve follow-up question retrieval | Original question retained |
| P1 | RAG-05 | Cross-encoder reranking | Improve ordering of retrieved candidates | Benchmark on Intel Mac / shared environment |
| P1 | RAG-06 | Evidence sufficiency/abstention gate | Reduce unsupported answers | Calibrate with evaluation dataset |
| P1 | RAG-07 | Citation validation | Ensure claims cite retrieved source/page evidence | Stable citation identifiers |
| P1 | EVAL-02 | Automated regression evaluation | Compare baseline and enhanced metrics | Dataset/report versioning |
| P2 | DOC-01 | OCR for scanned PDFs | Support image-only documents | Separate phase; not in initial RAG/UI scope |
| P2 | DOC-02 | Scheme date/version governance | Reduce stale document risks | Add issuer/year/effective dates/supersedes |
| P2 | AG-01 | Deterministic eligibility rules engine | More explicit, auditable scheme checks | Requires structured official criteria and legal/product review |
| P2 | AG-02 | Official source links | Enable users to verify details | Store verified government URLs |
| P2 | USER-01 | Persistent chat and consent | Retain user history under clear controls | Privacy/retention design |
| P3 | SEC-01 | Authentication and role-based access | Protect contributor/admin functions | Required before public multi-user deployment |
| P3 | OPS-01 | Monitoring, audit and deployment hardening | Operability beyond local demo | Security, secrets, backups, HTTPS, limits |
| P3 | ACCESS-01 | Voice input/output | Better accessibility for voice-first users | Human-review language quality |

## Proposed delivery sequence

1. **Requirements freeze:** approve UI/UX spec, FRD, architecture, RTM and acceptance thresholds.
2. **Isolated project bootstrap:** create code/dependency files only in `guru_ai_enhancements`; reuse `venv312`; create separate configuration and storage.
3. **P0 UI foundation:** implement and test Field to Future design tokens, dropdowns, contrast, responsive layout and baseline capability regression.
4. **Evaluation first:** create dataset and capture baseline RAG report using the enhanced project's isolated copy of permitted source documents.
5. **Hybrid retrieval:** BM25 + FAISS + RRF and metadata handling.
6. **Query rewriting and reranking:** add context rewrite and cross-encoder in separately testable stages.
7. **Evidence gate and citations:** calibrate abstention and validate evidence linkage.
8. **Acceptance and release candidate:** compare reports and obtain user acceptance.

The sequence is a proposed plan. The product owner can reprioritise or split phases through a change request.
