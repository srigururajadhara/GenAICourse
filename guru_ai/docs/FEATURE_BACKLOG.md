# Guru — Proposed Feature Backlog (Not Approved)

**Important:** This is a recommendation list only. None of these enhancements is authorised for implementation yet.

| ID | Proposed feature | Why it matters | Suggested implementation | Priority recommendation |
|---|---|---|---|---|
| ENH-001 | Hybrid retrieval (FAISS + BM25) | Semantic search can miss exact scheme names, acronyms, section numbers and amounts | Add BM25 keyword retrieval; combine rankings with reciprocal-rank fusion; keep source metadata | High |
| ENH-002 | Reranking | Improve relevance of passages passed to the LLM | Add a cross-encoder reranker after initial retrieval; evaluate on a labelled dataset | High |
| ENH-003 | Retrieval confidence/abstention gate | Reduce answers generated from weak or irrelevant matches | Calibrate retrieval thresholds using a test corpus; abstain when evidence is insufficient | High |
| ENH-004 | OCR for scanned PDFs | Many government PDFs are scans | Detect pages with low/no text; OCR with Tesseract or a managed OCR service; preserve page mapping | High |
| ENH-005 | Scheme version/effective-date management | Schemes change; outdated rules can mislead users | Store issuing authority, scheme year, publication date, effective-from/to, supersedes and source URL; prefer current valid documents | High |
| ENH-006 | Deterministic eligibility rules engine | Prompt-only eligibility guidance is not a verified decision engine | Convert official eligibility criteria into versioned structured rules; show each rule, evidence, result and missing field; keep human/department decision disclaimer | High |
| ENH-007 | Contextual query rewriting | Follow-ups such as “what documents are needed for this?” may retrieve poorly | Rewrite standalone query from chat context before retrieval; retain original question for audit | High |
| ENH-008 | Persistent chat history and user consent | Current chat is lost after session/restart | Add SQLite/PostgreSQL, session IDs, retention policy, delete/export controls and consent | Medium |
| ENH-009 | Authentication and role-based access | Upload/query endpoints are not protected for public deployment | Add authentication, contributor/admin roles, protected ingestion, rate limiting and audit logs | High before public release |
| ENH-010 | Document governance dashboard | Prevent duplicate, untrusted or obsolete documents | Document approval status, issuer/source URL, checksum, duplicate detection, update/retire/delete workflow | High |
| ENH-011 | Official-source verification links | Users need a path to verify details with the authority | Capture verified government source URL and show it alongside document/page citations | Medium |
| ENH-012 | Automated RAG evaluation | No systematic way to compare retrieval or prompt changes | Curate gold Q&A set; run regression tests; track Recall@K, MRR, groundedness, citations, latency and cost | High |
| ENH-013 | Prompt-injection and upload security controls | Uploaded documents and user queries are untrusted inputs | Treat retrieved text as data; add file-type/content checks, limits, scanning, prompt-injection tests and safe logging | High before public release |
| ENH-014 | Voice input and text-to-speech | Helps users who prefer speaking or have low literacy | Add speech-to-text and text-to-speech with language-specific evaluation and explicit consent | Medium |
| ENH-015 | Answer export/share | Useful for taking scheme information to an office or advisor | Generate downloadable PDF/print view with question, answer, document names, pages and timestamp | Low/Medium |
| ENH-016 | Admin monitoring and observability | Helps diagnose failed ingestion, API costs and poor answer quality | Structured logs, error tracking, latency/token/cost metrics and health checks | Medium |
| ENH-017 | Deployment hardening | Needed beyond local demonstration | Docker health checks, pinned runtime, secrets manager, HTTPS, backups, resource limits and CI pipeline | High before public release |

## Recommended delivery phases (proposal only)

1. **Trust and retrieval:** ENH-001, ENH-002, ENH-003, ENH-007 and ENH-012.
2. **Document quality and correctness:** ENH-004, ENH-005, ENH-006 and ENH-010.
3. **Security and real usage:** ENH-009, ENH-013, ENH-016 and ENH-017.
4. **User experience:** ENH-008, ENH-011, ENH-014 and ENH-015.

The phases are recommendations, not approved commitments. Public deployment should not precede the security, privacy, document governance and answer-quality work appropriate to the intended use.
