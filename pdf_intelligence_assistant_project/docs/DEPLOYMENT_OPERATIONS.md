# Deployment and Operations Requirements

## 1. Deployment approach

Use Docker for repeatable packaging. The UI, API and ingestion worker may run as separate services so that long PDF jobs do not block interactive requests. Local development may use a simpler compose setup; production topology depends on the deployment decision record.

## 2. Configuration and secrets

- Validate all required environment variables at startup.
- Keep `.env` local and ignored; provide `.env.example` with placeholders only.
- Use a secret manager or protected runtime secrets in production.
- Separate development, test and production credentials/databases/index namespaces.
- Never print API keys, Neo4j credentials or full signed storage URLs in logs.

## 3. Health and readiness

Expose separate health/readiness status for:
- API process;
- metadata database (if adopted);
- private file/object storage;
- FAISS index manifest and persistence path;
- BM25 index;
- Neo4j connectivity and schema/index readiness;
- OpenAI model/embedding connectivity (with safe timeout and no secret leakage);
- ingestion worker/queue.

Liveness should indicate process health; readiness should indicate whether the instance can safely serve its assigned role.

## 4. Observability

Capture structured, correlation-linked events for upload, extraction, OCR, vector indexing, BM25 indexing, graph extraction, graph write, retrieval channels, fusion, answer validation, export and deletion. Record duration, status, counts and safe error codes. Avoid logging entire PDFs, prompts containing sensitive data, API keys or full answer evidence by default.

Track at least:
- uploads and rejection reasons;
- page counts and extraction quality;
- queue depth, retries and stage durations;
- vector/BM25/graph pipeline success rate;
- Q&A latency, retrieval counts and abstention rate;
- model tokens and estimated cost;
- citation-validation failures;
- authorization denials and suspicious activity.

## 5. Backup and recovery

- Back up original PDFs, metadata database, Neo4j graph and index manifests according to approved retention policy.
- Ensure vector/lexical indexes can be rebuilt from canonical extracted content and manifests.
- Test restore procedures on a separate environment.
- Define recovery point and recovery time objectives before launch.
- Never restore one user's data into another workspace namespace.

## 6. Deletion

A delete operation shall track completion across originals, metadata, FAISS, BM25, Neo4j, derived summaries, exported files and caches. If any store fails, report deletion as pending and retry. Backup expiry follows the approved retention policy. The user must not be told that deletion is complete until all applicable live stores confirm it.

## 7. Release pipeline

1. Static analysis, formatting, type checks and dependency/security scans.
2. Unit and integration tests.
3. Golden-set RAG and citation evaluation.
4. Prompt-injection, authorization and tenant-isolation tests.
5. Docker build and container smoke tests.
6. Staging deployment and realistic load testing.
7. Backup/restore and deletion verification.
8. Release approval and rollback plan.

## 8. Operational runbook topics

- OpenAI timeout/rate limit or credential failure.
- Neo4j unavailable or graph schema mismatch.
- FAISS/BM25 index missing, corrupt or stale.
- Partial dual-pipeline ingestion and safe retry.
- OCR failure or extraction quality below threshold.
- Queue backlog and stuck jobs.
- Document deletion partially failed.
- Suspected cross-tenant leak or prompt injection incident.
- Backup restore and rollback.
