# Implementation status — v0.1.0

## Implemented in this source package

- FastAPI document, Q&A, summary, status, retry, extraction-approval and deletion endpoints.
- API-key-to-workspace authentication boundary; workspace-scoped metadata and local index paths.
- PDF signature/extension/content-type/file-size/page-count checks; encrypted/corrupt PDF rejection.
- Page-aware PyMuPDF extraction; optional Tesseract OCR for text-poor pages.
- Extraction review gate: low native-text yield, OCR-derived text and OCR failures pause indexing until explicit user review/approval.
- Canonical extraction JSON and stable provenance-aware chunk IDs.
- OpenAI embeddings with LangChain FAISS persistence.
- BM25 lexical index over the same chunk set.
- Typed entity/relation extraction prompt; allowlisted schemas; exact evidence quote checks.
- Neo4j nodes/edges with workspace/document/version/chunk/page provenance; parameterized read-only graph retrieval templates.
- Three-channel FAISS + BM25 + Neo4j retrieval and Reciprocal Rank Fusion (RRF).
- Context-aware follow-up query rewriting (optional configuration).
- LLM-grounded Q&A, answer citation ID checks and a separate evidence verification pass.
- Hierarchical map/reduce document summaries with citation IDs and a verification pass.
- Streamlit upload, pipeline statuses, extraction review, summaries, chat, evidence viewer and deletion controls.
- Audit events for upload, extraction review/approval, ingestion completion and deletion lifecycle.
- Dockerfile, Compose topology, sample-document golden set and offline test suite.

## Validation performed in the packaging environment

- Python syntax compilation passed.
- API module import and FastAPI smoke checks passed.
- The provided sample PDF parsed as 6 pages and produced 96 page-aware blocks and 96 initial chunks with no extraction warnings in this environment.
- Offline pytest suite: 22 tests passed, including simulated low-text extraction review/approval and follow-up query rewriting.
- See `VALIDATION_REPORT.md` for the exact test environment and checks not executed.

## Not yet validated

- Real OpenAI embedding, completion, graph extraction or model-verification calls.
- Real Neo4j schema creation, writes, reads, deletion and restart recovery.
- Full FAISS persistence/reload against the user's shared Python 3.12 environment.
- Full FastAPI + Streamlit runtime integration on the user's Mac.
- Multi-user OIDC/SSO and production identity lifecycle.
- Production-grade durable queue, PostgreSQL, object storage, TLS ingress, rate limiting, malware scanning, backups and restore testing.
- Load, penetration, adversarial prompt-injection and formal quality evaluation gates.

This is a runnable implementation baseline for local integration validation, not a production release certification.
