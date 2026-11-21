# RAG, Graph and Guardrail Evaluation Strategy

## 1. Purpose

Evaluate the complete system, not only whether the LLM produces fluent prose. Every run must be reproducible and tied to document version, parser, chunker, embedding model, index manifest, graph schema, prompt and LLM versions.

## 2. Evaluation dataset design

Create a versioned golden set from the uploaded sample PDF and later a representative set of permitted PDFs. Include:

- **Direct lookup:** exact facts, names, service lists and technologies.
- **Semantic lookup:** same concept expressed with different wording.
- **Exact-term retrieval:** acronyms, class names, routes, component names and numerical values.
- **Multi-hop / graph questions:** relationships across architecture sections.
- **Summary coverage:** executive, section and detailed summary tasks.
- **Ambiguous questions:** terms with multiple plausible meanings.
- **Unanswerable questions:** information absent from the selected document.
- **Conflicting statements:** multiple passages that appear inconsistent.
- **Adversarial prompts:** prompt injection in question or PDF content.
- **Scope attacks:** questions attempting to retrieve other documents/workspaces.

Each answerable item should include expected answer facts, acceptable page references, supporting chunks, expected entity/relation paths where relevant, and evaluation rubric.

## 3. Metrics

### Retrieval
- Precision@K and Recall@K against labelled supporting chunks.
- MRR and nDCG@K for ranking quality.
- Compare FAISS-only, BM25-only, graph-only (where applicable) and fused retrieval.
- Measure performance by question type and PDF type.

### Answer quality
- Faithfulness/groundedness: every factual claim supported by cited evidence.
- Answer relevance and completeness against reference answer facts.
- Unsupported-claim rate.
- Abstention precision/recall for unanswerable questions.
- Human review for a sample of automated-judge results.

### Citation quality
- Citation presence rate.
- Correct document/version/page rate.
- Evidence-to-claim support rate.
- Citation completeness for multi-page answers.

### Knowledge Graph
- Entity precision, recall and F1 against labelled mentions.
- Relation precision, recall and F1 against labelled assertions.
- Evidence provenance validity rate.
- Entity-resolution false-merge and false-split rates.
- Query correctness for graph test cases.

### Guardrails and security
- Prompt-injection detection/handling success and false-positive rate.
- Cross-workspace/document leakage count (target zero).
- Unauthorized file and graph access success count (target zero).
- Unsupported question abstention performance.
- Malformed/oversized PDF rejection and parser resource-control results.

### Operations
- Upload and ingestion duration by page count and file type.
- Pipeline success/failure/retry rates.
- Q&A p50/p95 latency and token/cost usage.
- OCR processing rates and confidence distribution.

## 4. Evaluation methodology

1. Create a human-reviewed golden set; do not use only LLM-generated references.
2. Establish baseline results for each retrieval channel independently.
3. Evaluate RRF against the individual channels and tune using a held-out set.
4. Compare optional reranker against RRF-only; keep disabled if it does not improve quality enough to justify latency/cost.
5. Evaluate graph extraction independently before trusting graph retrieval.
6. Score generated answers with deterministic citation checks plus an evaluation rubric and human spot checks.
7. Run all regression tests after any change to parser, splitter, embedding, schema, prompts, models or retrieval configuration.
8. Store results and configuration metadata; compare against the last approved release.

## 5. Initial proposed gates

These are proposed targets and must be confirmed after a baseline run:

- Recall@5 ≥ 0.85 on answerable retrieval questions.
- Citation page accuracy ≥ 0.90.
- Groundedness pass rate ≥ 0.90 on answerable questions.
- 100% of known unanswerable test questions either abstain or explicitly identify insufficient document evidence.
- 100% of tested cross-tenant/document-scope attacks blocked.
- Graph extraction precision target ≥ 0.90 before graph facts can be used as standalone evidence; relation recall can be tuned without lowering precision below the agreed threshold.
- No critical/high security issue open for release.

Do not optimize to metric thresholds by leaking answers into prompts or evaluation-time metadata. Separate tuning and test datasets.

## 6. Example sample-document questions

Use `SAMPLE_DOCUMENT_ANALYSIS.md` for source-grounded examples. Include questions such as:
- What frontend technologies are listed?
- Which databases/storage systems are described and what are their roles?
- What does the Playback & Session Service manage?
- Which microservices are listed in the architecture?
- Does the PDF specify an actual CEO salary? (Expected: no supporting information in this PDF.)
- Does the PDF specify a real company's deployed production architecture? (Expected: it describes a Spotify-like web application architecture; do not assert that it is Spotify's actual internal architecture.)

## 7. Reporting

Every evaluation report should state: dataset version/size, document set, run timestamp, model/prompt/index/schema versions, retrieval configuration, metric results, failed cases, cost/latency, human-review findings and release recommendation.
