# Guru Enhancements — Product Owner Approval Checklist

**Requirements pack:** v0.1  
**Current status:** Awaiting review  
**Implementation status:** Not started; no implementation authorised

Review each scope group. Approval can be for the full pack or a specified subset. Any item not approved remains out of implementation scope.

## A. Baseline and project rules

- [ ] Keep existing `guru_ai` untouched.
- [ ] Develop only in `guru_ai_enhancements`.
- [ ] Reuse shared `venv312`; do not create a new venv.
- [ ] Keep separate `.env`, PDFs, index, manifest, storage and test data.

## B. UX requirements

- [ ] Accept the Field to Future design direction.
- [ ] Require readable options in every open dropdown (the screenshot defect is P0).
- [ ] Require consistent readable contrast for all text, buttons, inputs, tabs, chat, citations and alerts.
- [ ] Require visible keyboard focus and keyboard operation.
- [ ] Require responsive desktop/tablet/mobile layout.
- [ ] Require original Guru-specific layouts/assets rather than a copied template.
- [ ] Accept proposed WCAG 2.2 AA target, subject to rendered contrast checks.

## C. Advanced RAG requirements

- [ ] Build a human-reviewed evaluation dataset and record baseline metrics first.
- [ ] Add BM25 lexical retrieval.
- [ ] Retain FAISS semantic retrieval.
- [ ] Combine ranked lists with RRF and deduplication.
- [ ] Add contextual query rewriting while preserving original question.
- [ ] Add a cross-encoder reranker after Intel Mac benchmarking.
- [ ] Add an evidence-quality / abstention gate with calibrated thresholds.
- [ ] Validate citations and preserve filename/page/state/category/chunk metadata.
- [ ] Add repeatable evaluation reporting.
- [ ] Retain English, Tamil, Hindi, Kannada, Telugu and Malayalam response options.

## D. Acceptance thresholds and open decisions

- [ ] Agree evaluation dataset starting size and reviewer process.
- [ ] Agree retrieval metrics and pass thresholds.
- [ ] Agree answer/citation quality and abstention thresholds.
- [ ] Agree acceptable p50/p95 latency and memory on target Mac.
- [ ] Approve reranker model after benchmark (not pre-selected in this pack).
- [ ] Approve browser/viewport support matrix.
- [ ] Approve whether a custom accessible dropdown component can be used if native menu styling is unreliable.

## E. Explicit authorisation

**Decision:** ☐ Approve all v0.1 requirements  ☐ Approve selected IDs only  ☐ Request changes  ☐ Defer

**Approved requirement IDs / groups:**  

**Conditions / changes requested:**  

**Approval statement:** “I approve the identified Guru Enhancements requirements for implementation in `guru_ai_enhancements`. The existing `guru_ai` project must remain untouched.”

**Approver:** Product owner  
**Date:**  
**Approved version:**

> Approval should be confirmed explicitly in the conversation or by completing this record. Until then, implementation remains blocked.
