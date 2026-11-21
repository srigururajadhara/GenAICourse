# Functional Requirements Document (FRD)

## 1. Scope and terminology

The application accepts PDF documents and offers document summaries and document-grounded Q&A. A **workspace** is the security and ownership boundary. A **document** is one uploaded PDF/version. A **chunk** is a source-linked text segment. A **claim/evidence item** is a passage or graph fact used to support an answer. A **document scope** is the currently selected document or explicitly selected set of documents.

## 2. Functional requirements

### A. Authentication, workspace and document scope

- **FR-001:** The system shall authenticate users before accessing private documents.
- **FR-002:** The system shall associate every document, index, graph node, chat session and export with a workspace/owner identifier.
- **FR-003:** The user shall select the active document scope before asking questions. The default scope shall be the currently opened document; multi-document querying must be explicit.
- **FR-004:** Retrieval shall enforce workspace and document scope at every retrieval backend, not only in the UI.
- **FR-005:** Users shall view their documents and ingestion status, and delete documents they own, subject to retention and audit policy.

### B. PDF upload and validation

- **FR-010:** The UI shall accept PDF files only.
- **FR-011:** The backend shall validate extension, MIME type and file signature; it shall not trust a filename or browser-provided content type alone.
- **FR-012:** The system shall enforce configurable file-size, page-count, processing-time and resource limits.
- **FR-013:** The system shall reject encrypted, malformed, corrupt or unsupported PDFs with a useful error unless an approved password-handling workflow is implemented.
- **FR-014:** The system shall calculate a content hash to identify exact duplicate uploads within the applicable ownership boundary.
- **FR-015:** The system shall retain the original file securely and record upload metadata, parser version and processing status.
- **FR-016:** A document-ingestion quality gate shall measure extracted text volume, empty pages and extraction anomalies; low-quality documents shall be flagged for OCR or user review.

### C. Content extraction and canonical representation

- **FR-020:** The system shall extract text with page boundaries and preserve page numbers.
- **FR-021:** The system shall preserve available headings, paragraphs, lists and tables as structured content where the PDF parser supports them.
- **FR-022:** Every extracted block shall retain document ID, version, page number and extraction provenance.
- **FR-023:** OCR shall be invoked only for pages classified as scanned or text-poor, and OCR-derived text shall be labelled with extraction method and quality/confidence metadata.
- **FR-024:** The system shall not silently discard low-confidence, unsupported or malformed content; it shall log and surface extraction warnings.

### D. Pipeline A — vector and lexical indexing

- **FR-030:** The system shall split canonical extracted content into configurable, structure-aware chunks.
- **FR-031:** Chunks shall preserve page references, section headings, offsets where available, document version and stable chunk IDs.
- **FR-032:** The system shall generate embeddings using the configured OpenAI embedding model.
- **FR-033:** The system shall store embeddings in a persistent FAISS index partitioned or filtered by workspace and document scope.
- **FR-034:** The system shall build a BM25 lexical index over the same canonical chunks.
- **FR-035:** The system shall support deterministic re-indexing and index version tracking.
- **FR-036:** A failed vector or lexical indexing stage shall not mark the document fully ready.

### E. Pipeline B — Knowledge Graph

- **FR-040:** The system shall extract entities using an approved typed schema, such as PERSON, ORGANIZATION, TECHNOLOGY, SERVICE, DATABASE, API, FEATURE, SECURITY_CONTROL and INFRASTRUCTURE_COMPONENT.
- **FR-041:** The system shall extract only relationships from an approved relationship schema, such as USES, DEPENDS_ON, STORES_DATA_IN, PROVIDES, AUTHENTICATES, PROCESSES, CONNECTS_TO and PART_OF.
- **FR-042:** Each entity mention and relationship shall preserve source document ID/version, page number, chunk ID, supporting text span/quote and extraction method.
- **FR-043:** The system shall validate entity and relationship types, endpoints, properties and evidence before graph storage.
- **FR-044:** Entity resolution shall avoid merging distinct entities solely because their display names are similar; ambiguous merges shall remain separate or require review.
- **FR-045:** Neo4j shall store graph data with document/workspace provenance and support controlled retrieval queries.
- **FR-046:** The LLM shall not execute unrestricted generated Cypher. Queries shall use approved templates, validated parameters, read-only credentials and result limits.
- **FR-047:** A graph extraction or storage failure shall be recorded separately; document readiness shall reflect the state of both pipelines.

### F. Hybrid retrieval and answer generation

- **FR-050:** For a user question, the system shall retrieve evidence from FAISS, BM25 and Neo4j graph search in parallel where applicable.
- **FR-051:** Graph results shall be resolved back to source-linked chunks/passages before being used as answer evidence.
- **FR-052:** The system shall fuse ranked evidence using Reciprocal Rank Fusion (RRF) with configurable weights or rank constants where supported.
- **FR-053:** An optional cross-encoder reranker may be evaluated; it shall remain disabled by default until quality, latency, cost and language coverage meet approved thresholds.
- **FR-054:** Retrieval shall apply document and workspace filters before evidence is passed to the LLM.
- **FR-055:** The system shall detect insufficient or conflicting evidence and abstain or explicitly describe the conflict.
- **FR-056:** The LLM shall answer using only supplied retrieved evidence; unsupported factual additions are prohibited.
- **FR-057:** Each answer shall cite document name/version and page number(s), with links to inspect the relevant extracted passages where possible.
- **FR-058:** Follow-up questions shall retain the active document scope and conversation context, but conversation history shall not override document evidence or access controls.

### G. Summarization

- **FR-060:** The user shall be able to request an executive summary.
- **FR-061:** The user shall be able to request a detailed summary and section-wise summary.
- **FR-062:** Summary statements shall be grounded in the uploaded document and include page references or section references.
- **FR-063:** The system shall distinguish facts stated in the document from inferences or recommendations; by default, it shall not add external facts.
- **FR-064:** If a summary is too long for one model context window, the system shall use a hierarchical/map-reduce strategy with intermediate provenance and a final verification pass.

### H. Guardrails and ingestion restrictions

- **FR-070:** The system shall treat uploaded PDF text as untrusted data, never as system/developer instructions.
- **FR-071:** The system shall detect and neutralize prompt-injection attempts in documents and user prompts using layered controls.
- **FR-072:** The system shall apply input validation, abuse limits and configurable content-safety checks.
- **FR-073:** The system shall reject or quarantine files that violate configured upload/security policies.
- **FR-074:** The system shall prevent out-of-scope knowledge from being injected into the prompt, including other users' files, unselected documents, hidden web context or unrelated sessions.
- **FR-075:** The final response validator shall check citation presence, citation-page validity and evidence support; failed checks shall trigger repair or abstention.

### I. Evaluation and quality assurance

- **FR-080:** The system shall maintain a versioned evaluation set containing answerable, multi-hop, exact-keyword, ambiguous and unanswerable questions.
- **FR-081:** Evaluation shall measure retrieval ranking, answer faithfulness/relevance, citation accuracy, graph extraction accuracy, guardrail effectiveness, abstention, latency and cost.
- **FR-082:** Evaluation shall support repeatable runs tied to model, prompt, embedding, chunking, index and graph-schema versions.
- **FR-083:** Production release shall require passing the approved test and evaluation gates.

### J. UI and operations

- **FR-090:** The UI shall provide PDF upload, document list, ingestion progress, document summary, chat/Q&A and citation inspection.
- **FR-091:** The UI shall show separate vector-index and graph-index status, plus a clear overall document readiness state.
- **FR-092:** The UI shall display actionable ingestion and retrieval errors without exposing secrets or stack traces.
- **FR-093:** The backend shall expose health and readiness checks for API, storage, FAISS, Neo4j and model connectivity.
- **FR-094:** The system shall produce structured logs with correlation IDs and stage-level timing, excluding raw sensitive document content by default.
- **FR-095:** The user shall be able to export summaries and Q&A where enabled, with citations preserved.

## 3. Non-functional requirements

- **NFR-001 Security:** Enforce authentication, authorization, least privilege, secure secrets, TLS in deployment, safe upload handling and dependency scanning.
- **NFR-002 Isolation:** No document, chunk, graph fact, cache entry or citation may cross workspace boundaries.
- **NFR-003 Reliability:** Ingestion stages shall be idempotent or safely retryable; partial failures shall be visible and recoverable.
- **NFR-004 Performance:** Establish measured latency budgets for upload, ingestion, summary and Q&A during baseline testing; do not promise throughput before load testing.
- **NFR-005 Scalability:** Separate API request handling from long-running ingestion jobs so workers can scale independently.
- **NFR-006 Observability:** Provide structured logs, metrics, traces/correlation identifiers and error reporting.
- **NFR-007 Maintainability:** Use modular services, typed schemas, configuration validation, automated tests and versioned prompts/indexes.
- **NFR-008 Accessibility:** Maintain readable contrast, keyboard navigation, clear focus states and responsive layout.
- **NFR-009 Data lifecycle:** Define retention, deletion, backup and restoration behavior before production deployment.
- **NFR-010 Cost control:** Track model tokens, embedding calls, OCR and graph extraction costs; cache only within correct ownership and document-version boundaries.

## 4. Requirement priority

- **P0:** Upload validation, canonical extraction/provenance, dual indexing, scoped hybrid retrieval, evidence-grounded Q&A, citations, guardrails, access isolation, baseline tests.
- **P1:** OCR, robust table extraction, hierarchical summaries, background workers, document/version management, exports, operational dashboards.
- **P2:** Advanced reranking, richer analytics, configurable schema packs and optional additional vector-store deployment.

## 5. Acceptance principle

A feature is not complete merely because it runs once. It must have requirement-linked tests, expected results, failure behavior and evidence from repeatable evaluation.
