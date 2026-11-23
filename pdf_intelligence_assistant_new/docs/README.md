# PDF Intelligence Assistant — Requirements & Architecture Pack v0.1

**Status:** Prepared for stakeholder review  
**Version:** 0.1  
**Date:** 21 November 2026  
**Purpose:** Approved planning deliverable; implementation has not started.

## What this project does

A user uploads a PDF, receives a document-grounded summary, and asks questions answered only from the selected uploaded PDF(s). The application builds two complementary knowledge representations:

1. **Vector / lexical pipeline:** PDF extraction → structure-aware chunking → OpenAI embeddings → FAISS vector index, with a BM25 index for exact-term retrieval.
2. **Knowledge Graph pipeline:** extracted document content → typed entity extraction → relation extraction and validation → Neo4j graph storage → controlled graph queries.

At question time, FAISS, BM25 and Neo4j retrieval contribute evidence to a hybrid retrieval process. Reciprocal Rank Fusion (RRF) combines ranked evidence, optional reranking can be benchmarked, and the LLM produces an answer with page-level citations. Guardrails and evaluations apply to ingestion, retrieval and generation.

## Pack contents

| File | Purpose |
|---|---|
| `PROJECT_CHARTER.md` | Goals, scope, stakeholders, success measures |
| `FRD.md` | Functional and non-functional requirements |
| `ARCHITECTURE.md` | Components, data flows, dual pipelines and hybrid retrieval |
| `DATA_AND_GRAPH_SCHEMA.md` | Metadata, chunk, entity and relationship model |
| `GUARDRAILS_SECURITY.md` | Ingestion controls, prompt-injection controls, privacy and access boundaries |
| `EVALUATION_STRATEGY.md` | Dataset, metrics, release gates and evaluation workflow |
| `RTM.md` | Requirements traceability to tests |
| `TEST_PLAN.md` | Functional, integration, security, performance and acceptance scenarios |
| `BACKLOG.md` | Prioritized implementation roadmap |
| `ASSUMPTIONS_DECISIONS.md` | Explicit assumptions, decisions and unresolved design choices |
| `DEPLOYMENT_OPERATIONS.md` | Deployment, monitoring, backup, recovery and release gates |
| `SAMPLE_DOCUMENT_ANALYSIS.md` | Facts and test-question seeds grounded in the uploaded sample PDF |

## Sample document

`sample_documents/spotify_web_app_architecture.pdf` is the six-page sample uploaded for initial implementation and testing. It describes a Spotify-like web application architecture; it is a test input, not a request to build a music-streaming product.

## Project boundaries

- This is a new, separate project. Existing `guru_ai` and `guru_ai_enhancements` projects must not be modified.
- The planned local environment is the user's existing `~/GenAICourse/venv312`. Dependency changes must be reviewed with `pip install --dry-run` before installation.
- No implementation code, local Mac integration testing, production deployment, or live security certification is included in this requirements pack.
- The pack recommends controls and defines acceptance criteria; it does not claim that any system is already secure or production validated.

## Approval workflow

1. Review this pack and resolve the open decisions in `ASSUMPTIONS_DECISIONS.md`.
2. Approve or request changes to scope and acceptance criteria.
3. Freeze requirements as v1.0 and start implementation in a new project directory.
4. Validate locally, run the test and evaluation gates, then perform security and deployment review.
5. Release only after explicit release approval.
