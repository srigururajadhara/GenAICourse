# Guru Enhancements — Test Plan

**Version:** 0.1  
**Status:** Draft; execution will start only after requirements approval and implementation  
**Date:** 15 November 2026

## 1. Test objectives

- Verify the Field to Future interface is readable, accessible and responsive.
- Prove that hybrid retrieval improves the baseline for the approved benchmark.
- Verify query rewriting preserves user intent and improves follow-up retrieval.
- Verify reranking improves evidence ordering.
- Verify evidence gating abstains when support is insufficient.
- Verify citations preserve and correctly reference the original PDF/page.
- Check performance and compatibility on the user's Intel Mac and shared Python 3.12 environment.

## 2. Test levels

| Level | Coverage |
|---|---|
| Unit | Query rewriting output handling, BM25 tokenisation/index, fusion, deduplication, rerank ordering, evidence gate, citation validation, design-token constants |
| Integration | BM25 + FAISS + fusion + reranking pipeline; API response schema; query rewrite fallback; index metadata |
| RAG quality | Recall@K, MRR/nDCG, precision, answer support, citation accuracy, completeness and abstention |
| UI | Open dropdown menus, labels, buttons, tabs, inputs, chat, loading/error/evidence states and responsive layout |
| Accessibility | Contrast, keyboard-only flow, focus visibility, selected/unselected state identification |
| Performance | Index time, query stage latency, reranker latency, total response time, memory and API cost |
| Regression | Existing upload/index, language, profile, chat, citations, eligibility disclaimer and KB views |
| Security/privacy | Prompt-injection cases in user query and retrieved PDF text; no secret/profile leakage in logs; isolated storage paths |

## 3. UI test scenarios

| Test ID | Scenario | Expected result |
|---|---|---|
| UX-TC-001 | Load enhanced dashboard | Field to Future identity is applied consistently; no copied template appearance |
| UX-TC-002 | Open State, Farmer type, Category, Irrigation and Answer language dropdowns | Every option is readable on its menu background in Chrome on macOS |
| UX-TC-003 | Inspect selected and unselected dropdown options | Selected option is distinct; unselected options remain readable; no dark-on-dark text |
| UX-TC-004 | Operate dropdown using keyboard | Open, navigate, select, dismiss; visible focus remains present |
| UX-TC-005 | Inspect all page text | Main content, sidebar, captions, alerts, hints, footer and evidence text meet approved contrast/readability rules |
| UX-TC-006 | Inspect suggested buttons in enabled and disabled states | Text is readable in both states; focus/hover/pressed states are clear |
| UX-TC-007 | Resize to approved desktop/tablet/mobile viewports | No clipped controls, hidden chat composer or unusable side panel |
| UX-TC-008 | Render user, assistant, error, loading and abstention messages | Different message states are understandable without colour alone |
| UX-TC-009 | Review all main sections | Profile, chat, library, upload and status components have clear hierarchy |
| UX-TC-010 | Upload/index and simulate API failure | Progress, success, empty and error messages are clear and actionable |
| UX-TC-011 | Review icons, fonts and illustrations | All assets are original or licensed and listed in the asset register |
| UX-TC-012 | Regression of baseline user journeys | Existing supported capabilities remain available unless specifically approved otherwise |

## 4. RAG test scenarios

| Test ID | Scenario | Expected result |
|---|---|---|
| RAG-TC-001 | Run the labelled test set against baseline before enhancement | Baseline report records metrics, versions, dataset and configuration |
| RAG-TC-002 | Ask using exact scheme name/acronym/section/amount keyword | BM25 retrieves chunks containing the matching term and useful context |
| RAG-TC-003 | Ask the same concept using paraphrased wording | FAISS semantic retrieval finds relevant passages |
| RAG-TC-004 | Combine lexical and semantic candidate lists | RRF ranking is reproducible; duplicate chunk IDs are removed |
| RAG-TC-005 | Ask state-specific and central-scheme questions | Applicable state and All India/central sources are retained appropriately |
| RAG-TC-006 | Compare ranking before and after reranker | Relevant gold passages move upward or approved relevance target is met; latency is recorded |
| RAG-TC-007 | Ask a context-dependent follow-up | Rewritten query includes required antecedent context and retrieves evidence for the intended scheme |
| RAG-TC-008 | Inspect original and rewritten query for each rewrite test | Original text is preserved; rewritten text does not add unsupported facts or alter intent |
| RAG-TC-009 | Ask a question absent from documents | System abstains and explains that uploaded evidence is insufficient |
| RAG-TC-010 | Run relevant and irrelevant evidence cases near threshold | Calibrated gate handles false accept and false abstain cases according to approved operating point |
| RAG-TC-011 | Verify each answer citation | Cited source/page is present in evidence and supports the associated claim |
| RAG-TC-012 | Trace metadata through all stages | Source file, page, state, category, document ID and chunk ID remain available |
| RAG-TC-013 | Generate evaluation report twice using fixed versions | Report is repeatable; any provider nondeterminism is noted |
| RAG-TC-014 | Run exact, paraphrase, follow-up, multilingual, state, ambiguous, out-of-corpus and conflict cases | Each test class has an observed result and review outcome |
| RAG-TC-015 | Ask in English, Tamil, Hindi, Kannada, Telugu and Malayalam | Response uses selected language while facts and citations remain source-grounded |
| RAG-TC-016 | Ask eligibility question with missing profile attributes | Guru lists missing data as “Needs verification”; no unsupported conclusion |
| RAG-TC-017 | Inspect diagnostic logs | Pipeline timing and errors are visible; secrets and unnecessary personal data are absent |

## 5. Evaluation dataset specification

Each benchmark record should contain:

- `case_id`
- original question
- optional prior-turn context
- expected standalone query intent (for follow-up cases)
- response language
- farmer state/profile fields when relevant
- expected document identifier and page(s), if answerable
- expected answer facts / key points
- answerability label: answerable, insufficient evidence, ambiguous, or conflicting sources
- query class: exact term, numeric fact, paraphrase, eligibility, process, checklist, state-specific, follow-up, multilingual, out-of-corpus, outdated/conflict
- reviewer and review date

Proposed starting size: 50–100 human-reviewed cases, expanded as failures are discovered. This is a planning recommendation, not an approved threshold.

## 6. Proposed metrics

| Dimension | Candidate measure | Notes |
|---|---|---|
| Retrieval | Recall@K, Precision@K | Requires gold relevant chunks/pages |
| Ranking | MRR, nDCG@K | Compare baseline, hybrid and reranked results |
| Answer | Human correctness/completeness score | Judge against source evidence, not general knowledge |
| Grounding | Claim support / groundedness review | Verify material claims against cited pages |
| Citations | Citation precision and citation coverage | Check both correctness and completeness |
| Abstention | False-accept rate and false-abstain rate | Threshold selected by risk trade-off |
| Follow-up | Query rewrite intent-preservation score | Human-reviewed labelled examples |
| Performance | p50/p95 latency by stage and total | Record model, hardware and index size |
| Cost | Embedding and generation usage/cost | Provider cost depends on account/pricing at run time |
| Operations | Failed requests and ingestion failures | Track by stage and error class |

Numerical pass thresholds are **TBD and require product-owner approval** before test execution.

## 7. Test data and safety

- Use official, permitted PDFs with known source/page references.
- Keep a small synthetic test corpus for unit tests, plus real official PDFs for acceptance tests.
- Include documents with conflicting or older versions to test cautious behaviour.
- Include malicious or instruction-like text in test documents to ensure retrieved text is treated as data, not trusted system instruction.
- Never put API keys in test fixtures or reports.

## 8. Exit criteria

The product owner must approve metric thresholds. A test cannot be marked Passed without recording environment, dependency versions, corpus/dataset version, result and evidence. No release is proposed until the approved UX checks and RAG acceptance criteria pass.
