# Security and production release gate

## Controls implemented in v0.1.0

- PDF extension, declared content type and `%PDF-` signature validation.
- Configurable file-size and page-count caps; encrypted and invalid PDF rejection.
- Server-generated document IDs and sanitized filenames.
- Authenticated API access using an API-key-to-workspace mapping.
- Workspace/document scoping in repository methods, vector directory layout and graph queries.
- Selected document is explicit for Q&A and summaries.
- No raw LLM-generated Cypher; graph retrieval uses parameterized read-only query templates.
- Entity and relationship types are allowlisted; exact verbatim quote, entity endpoint and predicate checks precede graph storage.
- Uploaded PDF text and chat history are treated as untrusted evidence, not instructions.
- Low-native-text and OCR-derived extraction is held for explicit user review before either knowledge index is built.
- Questions are length-checked and common prompt override / cross-workspace access attempts are rejected.
- LLM output citations must refer to retrieved chunk IDs; a separate verifier is called before returning factual answers/summaries.
- Secrets are environment-based; `.env` is ignored by Git.
- Delete endpoint removes local files/indexes and graph nodes; incomplete graph deletion is surfaced as pending rather than reported as success.

## Production blockers — must close before public/live release

1. **Identity:** integrate the approved OIDC/SSO or enterprise identity provider; add session lifecycle, roles, revocation, MFA policy and identity audit.
2. **Metadata:** replace local SQLite with PostgreSQL or another approved durable store for multi-instance operation.
3. **Object storage:** replace local upload storage with a private encrypted object store; define retention and legal hold.
4. **Background processing:** replace in-process FastAPI background tasks with a durable job queue and independently scaled workers; make all stages idempotent.
5. **Network/API security:** terminate TLS, enforce HSTS/security headers, rate limits, request timeouts, restrictive CORS, reverse-proxy body limits and abuse monitoring.
6. **Malware and parser isolation:** use approved malware scanning and process untrusted PDFs in a resource-limited worker/container without unnecessary network/filesystem privileges.
7. **Neo4j least privilege:** separate ingestion write credentials from read-only query credentials; configure private network access, backups and restore.
8. **FAISS artifact security:** protect FAISS persistence files and LangChain pickle docstore so only the trusted application service can write/read them; evaluate a non-pickle persistence option before shared multi-user hosting.
9. **Data governance:** approve what is sent to OpenAI, provider terms/region/retention, allowed document categories, data residency, PII handling and deletion policy.
10. **Observability:** central structured logs, metrics, traces, cost tracking, alerting and redaction review.
11. **Quality:** human-reviewed golden set, retrieval/answer/citation/graph-extraction/abstention thresholds, multilingual tests and regression baselines.
12. **Security verification:** cross-workspace IDOR tests, graph/vector isolation tests, direct/indirect prompt-injection tests, file/parser abuse tests, dependency scan, secrets scan and penetration test.
13. **Operations:** encrypted backups and tested restore, disaster-recovery targets, rollback, deployment runbook and incident response.
14. **Scale:** concurrency and load testing; establish measured SLOs and cost-per-document/query.

## Release stop conditions

- Never mark a document `READY` unless both vector and graph pipelines complete successfully.
- Never index low-text or OCR-uncertain extraction without an explicit review-and-approval step.
- Never pass graph facts to the LLM without a supporting page/chunk.
- Never let a user query execute generated Cypher or arbitrary tools.
- Never answer from another document/workspace or from public model knowledge.
- Never report successful deletion until all required stores confirm cleanup.
- No open critical/high security findings at production release.
- No production release solely on the basis of offline unit tests.

The release remains blocked until all production blockers are addressed, tested and explicitly approved.
