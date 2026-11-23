# Assumptions, Decisions and Open Questions

## 1. Confirmed from the user's request

- The new application is a PDF upload, summarization and document-grounded Q&A assistant.
- It uses two ingestion pipelines: (A) data loader → text splitter → embeddings → vector DB; (B) graph data loading → entity extraction → relationship mapping → graph storage → graph query.
- Hybrid RAG is required.
- Guardrails and evaluations must restrict unwanted context and ingestion.
- The uploaded sample PDF is `spotify_web_app_architecture.pdf`.
- The same general technology direction as Guru AI is preferred.
- The project is intended for a live/production deployment, so security, testing, monitoring and operations are in scope.

## 2. Proposed defaults

| Area | Proposed default | Reason / caveat |
|---|---|---|
| Frontend | Streamlit | Consistent with Guru AI and fast to iterate; assess UX/concurrency limits before production scale |
| Backend | FastAPI | Separate API and UI; supports typed request validation |
| LLM | OpenAI GPT-4o-mini | Same model family as Guru AI; verify current availability and terms at implementation time |
| Embeddings | Configurable OpenAI embedding model | Exact model ID/dimensions frozen after compatibility and cost test |
| Vector index | FAISS | Reuse Guru AI approach; persistence/metadata filtering and multi-instance deployment need explicit design |
| Keyword index | BM25 | Exact-match retrieval for terms, identifiers and component names |
| Graph | Neo4j | Explicit user requirement and graph query support |
| PDF parser | Benchmark PyMuPDF and PyPDF on sample corpus | Choose based on extraction quality, tables, page metadata and licensing |
| OCR | Tesseract initially, subject to benchmark | OCR only on scanned/poor-text pages; language pack requirements must be known |
| Fusion | RRF | Combines ranks without comparing incomparable raw scores |
| Reranker | Disabled by default | Enable only after measured quality/latency/cost approval |
| Containers | Docker | Reproducible deployment and service isolation |

## 3. Open decisions before implementation freeze

| ID | Decision needed | Proposed choice / decision gate |
|---|---|---|
| D-001 | Authentication provider | Choose existing identity provider or simple managed OIDC; do not build custom password handling without need |
| D-002 | Metadata and job database | PostgreSQL recommended for production document/user/job metadata; confirm infrastructure availability |
| D-003 | Original PDF/object storage | Private local volume for local development; S3-compatible object storage for production |
| D-004 | Background job system | Queue/worker recommended for production; select Redis-backed queue or another approved broker after deployment needs are known |
| D-005 | Deployment target | Confirm cloud/VPS/on-prem, network boundaries, region and expected concurrency |
| D-006 | Data retention/deletion | Define retention, backups, legal hold and deletion behavior before production use |
| D-007 | PDF limits | Confirm max file bytes, page count, pages/minute and concurrent jobs based on load testing |
| D-008 | Supported PDF languages | Confirm initial language scope and OCR language packs |
| D-009 | OCR provider | Benchmark Tesseract vs managed OCR if scanned PDFs are common or table fidelity is critical |
| D-010 | Embedding model | Freeze exact model ID after tests for English and any required other languages |
| D-011 | Neo4j hosting | AuraDB vs self-hosted; confirm tenant strategy, backup and network access |
| D-012 | User data sent to OpenAI | Approve provider terms, data region/retention requirements and disclosure to users |
| D-013 | Allowed content policy | Define any prohibited categories or confidentiality restrictions; default is general PDF processing with scope-only answering |
| D-014 | Expected load/SLO | Confirm users, concurrent uploads/queries and target response time before capacity sizing |

## 4. Explicit safeguards against assumptions

- Do not assume the sample PDF describes Spotify's actual internal systems; it is titled and framed as a Spotify-like web app architecture.
- Do not infer undocumented details, relationships or implementation choices from the sample.
- Do not treat a graph extraction candidate as a verified fact until source-evidence validation passes.
- Do not claim production readiness from local functional tests alone.
- Do not upgrade the shared `venv312` until a dependency dry run has been reviewed.
- Do not modify `guru_ai` or `guru_ai_enhancements`.

## 5. Change control

Any feature or architecture change that affects scope, security boundaries, storage, cost, retention, user data handling or release criteria must be recorded as a change request and approved before implementation.
