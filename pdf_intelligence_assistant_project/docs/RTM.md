# Requirements Traceability Matrix (RTM)

| Requirement IDs | Requirement summary | Primary component | Verification |
|---|---|---|---|
| FR-001–005 | Authentication, ownership and selected document scope | API/auth/document service | TST-001–006, SEC-001–006 |
| FR-010–016 | Upload validation, secure storage, duplicate and extraction quality checks | Upload/document/extraction services | TST-010–018, SEC-010–014 |
| FR-020–024 | Page-aware canonical extraction, structure and OCR provenance | PDF extraction | TST-020–026 |
| FR-030–036 | Chunking, embeddings, FAISS, BM25 and index lifecycle | Vector/lexical indexer | TST-030–037, EVAL-001–006 |
| FR-040–047 | Typed entity/relation extraction, provenance, Neo4j and safe graph query | Graph pipeline | TST-040–049, EVAL-010–014, SEC-020–024 |
| FR-050–058 | Parallel retrieval, RRF, evidence thresholds, answer and citations | Retrieval/Q&A | TST-050–061, EVAL-020–030 |
| FR-060–064 | Executive, detailed, section and hierarchical summaries | Summary service | TST-060–068, EVAL-031–036 |
| FR-070–075 | Prompt injection, scope, evidence and output guardrails | Guardrail service | SEC-030–041, EVAL-040–047 |
| FR-080–083 | Versioned evaluation and release gates | Evaluation service/CI | EVAL-001–050 |
| FR-090–095 | UI, progress, status, health, logs and exports | UI/API/operations | TST-070–080, OPS-001–010 |
| NFR-001–010 | Security, isolation, reliability, performance, maintainability, accessibility, lifecycle and cost | Cross-cutting | Security, load, recovery and usability test reports |

## Traceability rule

Every approved requirement must map to at least one test case and one implementation component. Any requirement without verification is a release blocker or an explicitly accepted, documented risk. Test IDs are defined in `TEST_PLAN.md` and may be expanded during implementation.
