# Prioritized Product Backlog

## P0 — Production foundation and core PDF assistant

1. Project skeleton, configuration and secret handling.
2. Authentication/authorization integration and workspace/document isolation.
3. PDF upload validation, private storage, hash and document version records.
4. Page-aware text extraction and canonical document representation.
5. Structure-aware chunking with stable IDs and provenance.
6. FAISS embeddings/index persistence and BM25 lexical index.
7. Typed entity/relation extraction with provenance and validation.
8. Neo4j graph storage and controlled graph query templates.
9. Parallel FAISS/BM25/graph retrieval with evidence resolution and RRF.
10. Evidence thresholds, conflict detection, abstention and citation validation.
11. Executive, detailed and section summaries.
12. Streamlit UI: upload, processing status, document view, summary, chat and citations.
13. Guardrail, unit, integration, isolation and golden-set evaluation suite.
14. Docker packaging, health checks, structured logs and basic metrics.

## P1 — Document quality and operational completeness

1. OCR for scanned pages with provenance and quality thresholds.
2. Table-aware extraction improvements and extraction review UI.
3. Background ingestion worker/queue and retry dashboard.
4. Document version comparison, duplicate management and safe rebuild.
5. Export summary/Q&A to PDF or DOCX with citations.
6. Admin operational dashboard, metrics and audit events.
7. Backup/restore automation and deletion verification.
8. Load/performance tests and cost monitoring.

## P2 — Measured enhancements

1. Cross-encoder reranking after multilingual/quality/latency/cost benchmarks.
2. Query decomposition for complex multi-hop questions.
3. More advanced graph summarization and graph visualization.
4. Configurable extraction ontologies for different PDF domains.
5. Additional vector-store option if production scale or concurrency requires it.

## Definition of done

A backlog item is done only when its code, configuration, requirement mapping, automated tests, error handling, logs/metrics (where applicable), documentation and acceptance evidence are complete. Features with unapproved scope changes require a change request.
