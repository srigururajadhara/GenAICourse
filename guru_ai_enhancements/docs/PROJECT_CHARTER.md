# Guru Enhancements — Project Charter

**Version:** 0.1  
**Status:** Draft for approval  
**Date:** 15 November 2026

## 1. Project purpose

Enhance Guru from a working agricultural-scheme PDF RAG assistant into a more usable, measurable and evidence-reliable application while protecting the existing working baseline.

## 2. Product vision

Help farmers and agricultural support users understand government scheme information in accessible language, with every material answer traceable to uploaded source documents and page evidence. Guru is an information assistant, not a government authority or application-submission service.

## 3. Objectives

1. Establish a distinctive, readable and accessible Guru user experience.
2. Improve retrieval of both exact terms (scheme names, acronyms, amounts, section numbers) and semantically similar wording.
3. Improve multi-turn question handling so follow-up questions are understood in context before retrieval.
4. Improve relevance ordering of retrieved passages.
5. Avoid unsupported answers by introducing evidence-quality checks and a controlled abstention response.
6. Create repeatable evaluation data and measurements before and after RAG changes.
7. Preserve source, page, state and category metadata through the retrieval and answer pipeline.
8. Keep enhancement development isolated from the existing `guru_ai` project.

## 4. Scope

### In scope for the requirements phase

- Baseline and gap documentation based on the reviewed project source snapshot.
- UX requirements, including the dropdown visibility defect and the accepted Field to Future design direction.
- Advanced RAG requirements for hybrid search, reranking, contextual query rewriting, evidence validation/abstention and evaluation.
- Proposed architecture, RTM, test plan, prioritised backlog, approval process and baseline-protection controls.
- A documentation-only folder scaffold for `guru_ai_enhancements`.

### Candidate implementation scope after approval

- New UI design system and reusable UI components.
- New retrieval orchestration with query rewrite, BM25 + FAISS, rank fusion and reranking.
- Evidence quality/abstention handling.
- RAG evaluation harness and regression dataset.

### Out of scope for this requirements pack

- Editing or upgrading the source code in the existing `guru_ai` project.
- Deploying a public production service.
- Building a deterministic scheme eligibility engine.
- OCR, voice interaction, persistent chat, authentication, official portal automation or application submission.
- Making legal determinations about scheme eligibility or guaranteeing benefits.

These remain later backlog candidates unless separately approved.

## 5. Stakeholders and responsibilities

| Role | Responsibility |
|---|---|
| Product owner / user | Owns priorities, reviews requirements, approves scope and accepts results |
| AI development assistant | Prepares designs, documentation, implementation proposals, code and test evidence after approval |
| User/tester | Runs the project on the local Mac, provides actual UI/API observations and confirms acceptance |
| Government department / scheme authority | Remains the authoritative source for current rules and final eligibility decisions; not a project delivery stakeholder |

## 6. Constraints and operating decisions

- Existing project: `GenAICourse/guru_ai` — protected; no writes.
- Enhancement project: `GenAICourse/guru_ai_enhancements` — separate working directory.
- Python environment: reuse `GenAICourse/venv312`; do not create another venv by default.
- Runtime/data: separate `.env`, PDF input, storage, index, manifest, logs and test fixtures for enhancements.
- Host environment is an Intel Mac with 16 GB RAM as previously described; candidate reranker must be benchmarked on this machine before a final model is selected.
- The requirements pack is documentation-only. Dependencies and code are not being changed.

## 7. Proposed success measures

Final thresholds must be agreed before implementation. The project should demonstrate measurable improvement over the baseline on a fixed evaluation set:

- Better retrieval of exact scheme identifiers and paraphrased queries.
- Better ranking of relevant passages near the top of results.
- Correct resolution of tested follow-up questions.
- Higher evidence/citation support and fewer unsupported answers.
- Predictable and acceptable latency/cost on the target machine.
- No regression in existing language, profile, source-page or API behaviours unless explicitly approved.
- 100% pass of approved UI dropdown readability and keyboard interaction acceptance cases.

## 8. Major risks

| Risk | Mitigation |
|---|---|
| Reranker too slow or memory-heavy on Intel Mac | Benchmark small CPU-capable models; keep model configurable; compare quality/latency |
| Hybrid retrieval introduces duplicate or irrelevant chunks | Use stable chunk IDs, deduplication and labelled evaluation |
| Confidence is misrepresented as probability | Calibrate thresholds; never label raw vector distance as probability |
| Rewriting changes user intent | Keep original question, log rewritten query, test against query-intent examples |
| Scheme PDF is outdated or incomplete | Preserve document metadata; flag date uncertainty; do not infer current status |
| UI styling differs across browser/platform | Test actual opened dropdown menus on supported browsers, not just closed controls |
| Baseline is accidentally modified | Separate paths, storage and environment variables; explicit baseline protection checks |

## 9. Governance

No enhancement implementation is authorised by this charter. The FRD and acceptance criteria must be reviewed and explicitly approved by the product owner before code changes begin.
