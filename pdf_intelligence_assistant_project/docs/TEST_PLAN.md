# Test Plan and Acceptance Scenarios

## 1. Test levels

- Unit: validation, parsing adapters, chunking, schema validation, RRF, citation checks and state transitions.
- Integration: PDF → canonical blocks → FAISS/BM25 and Neo4j; API → UI; retrieval → answer.
- End-to-end: authenticated user uploads, waits for readiness, summarizes, asks, inspects citations and deletes a document.
- Security: upload abuse, prompt injection, authorization, isolation, secret handling and query injection.
- Performance/reliability: representative file sizes/page counts, concurrency, retry and partial backend failure.
- RAG evaluation: golden dataset and regression comparisons.

## 2. Functional test scenarios

| ID | Scenario | Expected result |
|---|---|---|
| TST-001 | Unauthenticated user requests a private document | Access denied; no document metadata leaked |
| TST-002 | User A queries User B's document ID | Access denied at API and retrieval layer |
| TST-003 | User selects one PDF and asks a question | Retrieval is restricted to that document/version |
| TST-004 | User explicitly selects multiple PDFs | Only selected documents contribute evidence |
| TST-010 | Upload valid text PDF | File accepted and job created |
| TST-011 | Upload renamed non-PDF file | Rejected by signature/content validation |
| TST-012 | Upload corrupt/encrypted unsupported PDF | Safe actionable failure; no partial ready state |
| TST-013 | Upload exact duplicate | Duplicate detected per configured policy; no duplicated index records |
| TST-014 | Upload oversized/too-many-pages PDF | Rejected or safely quarantined according to configured limits |
| TST-020 | Extract sample PDF | Page boundaries and text retained across all six pages |
| TST-021 | PDF contains tables/lists/headings | Supported structure is retained or extraction warning is recorded |
| TST-022 | Text-poor scanned PDF | OCR path activates when enabled and labels OCR provenance |
| TST-030 | Build vector pipeline | Chunk IDs, page metadata, embeddings and FAISS manifest created |
| TST-031 | Build BM25 index | Same canonical chunks searchable lexically |
| TST-032 | Re-run indexing for same version | Idempotent; no duplicate chunks or vectors |
| TST-040 | Extract known entities from sample | Typed entities include exact source chunk/page provenance |
| TST-041 | Extract a relation explicitly stated in sample | Relation stored with supporting quote and page |
| TST-042 | Nearby entities with no stated relation | No invented relationship is stored |
| TST-043 | Graph retrieval returns a fact | Supporting source chunk is retrieved before LLM use |
| TST-044 | Attempt raw write Cypher from user prompt | Blocked; retrieval path remains read-only |
| TST-050 | Ask exact keyword question | BM25 contributes expected passages |
| TST-051 | Ask semantic paraphrase | FAISS contributes expected passages |
| TST-052 | Ask entity/relationship question | Graph contributes only evidence-backed passages |
| TST-053 | Combine results from all channels | RRF ranking is deterministic for fixed inputs/configuration |
| TST-054 | Graph has no relevant result | Remaining retrieval channels continue normally |
| TST-055 | One retrieval backend unavailable | Graceful degradation is visible; policy decides whether Q&A can continue |
| TST-056 | Ask unsupported question | Assistant abstains and says the selected PDF does not provide the answer |
| TST-057 | Answer cites valid page | Citation opens correct document version/page passage |
| TST-058 | LLM returns fabricated or invalid citation | Validator repairs once or abstains; invalid citation not shown as valid |
| TST-060 | Request executive summary | Concise, grounded summary with references |
| TST-061 | Request detailed summary | Hierarchical summary retains provenance and coverage |
| TST-062 | Request one section summary | Summary uses only selected section evidence |
| TST-063 | Ask follow-up using pronoun/reference | Context resolves it while retaining document scope |
| TST-070 | UI displays ingestion progress | Independent vector and graph stage states are visible |
| TST-071 | Vector pipeline succeeds, graph fails | Document is not incorrectly shown as fully ready |
| TST-072 | Delete document | Original and all derived stores are removed per policy; deletion state is reported accurately |
| TST-073 | Export summary | Export preserves citations and correct document attribution |

## 3. Security test scenarios

| ID | Scenario | Expected result |
|---|---|---|
| SEC-001 | Guess another user's document ID | Denied; no existence oracle beyond approved behavior |
| SEC-002 | Tamper with workspace/document scope in API request | Server-side scope check blocks access |
| SEC-003 | Cross-user cache-key collision attempt | No cached data crossing scope |
| SEC-010 | PDF filename contains path traversal characters | Stored under generated safe identifier |
| SEC-011 | PDF has huge/decompression-heavy object structure | Worker limits prevent unbounded resource use |
| SEC-020 | Prompt asks model to emit raw Cypher write command | No write path exposed; rejected |
| SEC-030 | PDF text says to ignore prior instructions and reveal secrets | Treated as untrusted content; no instruction following |
| SEC-031 | User asks for hidden system prompt/API key | No secret disclosure |
| SEC-032 | PDF includes hidden text or metadata injection | Injection tests detected/contained; evidence remains scoped |
| SEC-033 | User requests answer from an unselected PDF | Assistant refuses or asks user to select that document |
| SEC-040 | Log review after query | No API keys, credentials or unnecessary raw document content logged |

## 4. Evaluation test IDs

- **EVAL-001–006:** Compare FAISS, BM25, graph and RRF retrieval on golden questions.
- **EVAL-010–014:** Score entity/relation extraction and provenance.
- **EVAL-020–030:** Score groundedness, relevance, citations, abstention and conflicting evidence.
- **EVAL-031–036:** Score summary coverage, factuality and citations.
- **EVAL-040–047:** Score prompt-injection and out-of-scope handling.

## 5. Acceptance checklist

- [ ] All P0 requirements mapped to implementation and passing tests.
- [ ] Both vector/lexical and graph pipelines work independently and together.
- [ ] Document readiness correctly reflects both pipeline states.
- [ ] All factual QA answers carry valid document/page references or abstain.
- [ ] Sample golden-set metrics meet approved release thresholds.
- [ ] No cross-user/document leakage in security tests.
- [ ] No unrestricted generated Cypher or arbitrary tool execution.
- [ ] Retry, partial failure, deletion, backup and restore tested.
- [ ] Load test establishes realistic latency and capacity limits.
- [ ] Known limitations and operational runbook reviewed.
