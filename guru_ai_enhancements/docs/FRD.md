# Guru Enhancements — Functional Requirements Document (FRD)

**Version:** 0.1  
**Status:** Draft for product-owner review — implementation not authorised  
**Date:** 15 November 2026

## 1. Purpose

Define proposed requirements for the separate `guru_ai_enhancements` project. The requirements cover the new UI/UX direction and the Advanced RAG Phase 1 work agreed as the next enhancement track. The existing `guru_ai` project remains the protected baseline.

## 2. Current-state summary

The reviewed baseline is a Streamlit frontend backed by FastAPI. It accepts PDFs, extracts text using PyPDFLoader, splits pages into overlapping chunks, creates OpenAI embeddings, stores vectors in FAISS, retrieves using semantic similarity and uses GPT-4o-mini to formulate a grounded response. The answer payload includes citation metadata such as source file and page.

Current limitations relevant to this scope:

1. Retrieval is semantic FAISS similarity only; BM25 lexical retrieval is absent.
2. Retrieval runs against the latest question text; conversation history is added to generation context but is not used to rewrite follow-up queries before retrieval.
3. Reranking is absent.
4. There is no calibrated evidence-quality gate that decides when evidence is insufficient.
5. There is no fixed, labelled RAG evaluation set or repeatable quality report.
6. In the provided screenshot, the open Irrigation dropdown displayed dark green option text against a near-black menu background. The option list was not readable even though the selected item used a light background.
7. Existing UI styles do not yet define a complete reusable design system with consistent dropdown, focus, hover, disabled and responsive states.
8. The latest screenshot shows an uploader label of 200 MB per file, whereas the reviewed API source snapshot rejects files larger than 30 MB. The actual running backend setting must be verified before the enhancement upload-size requirement is baselined.

## 3. User classes and use cases

| User class | Primary use cases |
|---|---|
| Farmer / public user | Ask scheme questions, select farmer context, choose answer language, review source evidence |
| Knowledge contributor | Upload official scheme PDFs, tag source state/category, rebuild the knowledge base |
| Product owner / evaluator | Review quality metrics, inspect failures, approve changes and acceptance criteria |

No account management or role-based access control is included in this phase.

## 4. Requirement priority and status

Priority definitions:
- **P0:** Required for usability/readability and baseline protection before the enhanced experience is accepted.
- **P1:** Required for the Advanced RAG Phase 1 objective.
- **P2:** Valuable supporting requirement; not required for the first approved increment unless selected by the product owner.

All rows below are **Proposed** until approved. No requirement in this document authorises code changes by itself.

## 5. Functional requirements — UI/UX

| ID | Priority | Requirement | Proposed acceptance criterion |
|---|---:|---|---|
| UX-001 | P0 | The application shall implement the original Guru visual direction named **Field to Future**, with a distinct layout, typography, colour system, icon treatment and reusable components. | The interface uses the approved design tokens and original component layouts; it does not reproduce another named product's screen or template. |
| UX-002 | P0 | Every dropdown shall display readable text in its closed, open, selected, unselected, hover, focus and disabled states. | In Chrome on macOS, open every dropdown and verify each option label is readable against its background; no dark-on-dark option combinations. |
| UX-003 | P0 | Dropdown menus shall use a consistent high-contrast light menu surface with dark option text, with a distinct selected state. | All options, including the selected value and all other options, remain distinguishable when the menu is open. |
| UX-004 | P0 | Dropdowns shall support keyboard navigation and visible focus indication. | Tester can open, navigate, select and dismiss each dropdown using keyboard only; focus is visible. |
| UX-005 | P0 | Inputs, text areas, placeholders, labels, helper text, error text, tabs, status badges, buttons, chat messages, citations and footer text shall meet the approved contrast and readability rules. | No text is clipped, hidden or low-contrast at the supported viewport sizes; contrast checks meet the approved accessibility target. |
| UX-006 | P0 | Buttons shall have clearly distinguishable primary, secondary, hover, focus, pressed and disabled states. | Text remains readable in every state, including disabled suggested-question buttons. |
| UX-007 | P0 | The layout shall adapt to desktop, tablet and mobile widths without overlapping, horizontal clipping or inaccessible controls. | Test at the agreed desktop, tablet and mobile viewport sizes; all primary tasks remain usable. |
| UX-008 | P0 | The chat interface shall visually distinguish user messages, Guru responses, citations, loading states, errors and abstention responses. | Each message type is visually identifiable without relying on colour alone. |
| UX-009 | P0 | The farmer profile, document upload, knowledge-base status, Ask Guru, Eligibility guidance and Knowledge base functions shall have consistent spacing, labels and visual hierarchy. | A first-time user can identify each function and its current state without relying on hidden styling. |
| UX-010 | P0 | The application shall provide clear upload progress, ingestion success/failure messages, API status and empty-index states. | Empty, loading, success and error states include readable explanatory text and a next action. |
| UX-011 | P0 | Visual assets, icons, copy and component arrangements shall be selected or created for Guru and used under appropriate licences. | Asset inventory and attribution are documented; no copied proprietary UI or unlicensed assets are introduced. |
| UX-012 | P0 | The UI shall preserve the existing farmer-facing capabilities unless an approved change explicitly modifies them. | Regression tests cover profile fields, language selection, upload/index, chat, source evidence and eligibility guidance. |

## 6. Functional requirements — Advanced RAG

| ID | Priority | Requirement | Proposed acceptance criterion |
|---|---:|---|---|
| RAG-001 | P1 | The enhanced project shall establish a fixed, human-reviewed evaluation dataset before retrieval changes are compared. | Each test case includes question, language, state/context where relevant, expected source/page or expected abstention, and expected answer points. Baseline metrics are recorded before enhancement. |
| RAG-002 | P1 | The retrieval service shall perform lexical keyword retrieval using BM25 over indexed chunks. | Exact scheme names, acronyms, numeric references and distinctive keywords can be found in the labelled benchmark. |
| RAG-003 | P1 | The retrieval service shall perform semantic vector retrieval using FAISS. | Paraphrased and conceptually worded questions retrieve relevant evidence in benchmark cases. |
| RAG-004 | P1 | The service shall combine lexical and semantic result lists using a documented rank-fusion method, proposed as Reciprocal Rank Fusion (RRF). | Duplicate chunks are deduplicated; source/page metadata is preserved; fusion output is deterministic for a fixed input. |
| RAG-005 | P1 | The service shall support state/category metadata filtering or prioritisation without losing relevant All India evidence. | State-specific retrieval tests show relevant state documents and applicable All India sources are retained; filtering is not limited to post-filtering an insufficient semantic top-K result. |
| RAG-006 | P1 | The service shall rerank fused candidate passages using a configurable cross-encoder or equivalent relevance reranker. | Reranked top results are compared with pre-rerank results on the labelled dataset; relevance improves or the approved threshold is met without unacceptable latency. |
| RAG-007 | P1 | The service shall rewrite context-dependent follow-up questions into standalone retrieval queries using recent conversation turns. | Follow-up cases such as “what documents are needed for this?” retrieve evidence for the previously discussed scheme. |
| RAG-008 | P1 | The service shall preserve and use the user's original question for answer generation and audit, alongside the rewritten retrieval query. | The rewritten query does not replace or silently alter the original user intent; both values can be inspected in controlled diagnostics. |
| RAG-009 | P1 | The system shall assess evidence sufficiency before generating a factual answer and return a clear abstention response when support is inadequate. | Out-of-corpus, low-relevance and ambiguous cases are not answered with invented facts; the response explains the evidence gap. |
| RAG-010 | P1 | Evidence confidence thresholds shall be calibrated using the reviewed evaluation set; raw FAISS distance or a model's self-reported confidence shall not be represented as a probability. | Threshold selection is documented with false-accept/false-abstain analysis; no uncalibrated confidence percentage is displayed. |
| RAG-011 | P1 | The answer shall cite source identifiers, filenames and page numbers for material claims, using evidence actually supplied to generation. | Citation validation tests confirm each cited source/page exists in the retrieved evidence and supports the associated answer point. |
| RAG-012 | P1 | The system shall preserve source metadata through rewrite, retrieval, fusion, reranking, answer generation and display. | Source filename, page, state, category and stable chunk/document identifiers remain traceable end-to-end. |
| RAG-013 | P1 | The evaluation harness shall compute agreed retrieval, answer, citation, abstention, latency and cost measures. | A repeatable report compares the baseline and enhanced pipeline on the same versioned dataset. |
| RAG-014 | P1 | The evaluation set shall include exact-match facts, paraphrases, follow-ups, state-specific queries, multilingual questions, missing evidence, ambiguous questions and conflicting/outdated sources. | Every query class has approved test cases and expected behaviour. |
| RAG-015 | P1 | The enhanced RAG pipeline shall retain the existing language selection behaviour for English, Tamil, Hindi, Kannada, Telugu and Malayalam. | Each language is tested for answer language, source fidelity and citation retention; language quality is reviewed by a competent human reviewer. |
| RAG-016 | P1 | The enhanced pipeline shall not use farmer profile fields to invent missing scheme criteria or fill gaps in source evidence. | Test cases with incomplete profiles label unknown fields as requiring verification and do not infer eligibility. |
| RAG-017 | P1 | The system shall log diagnostic pipeline stages without logging secrets or unnecessary personal data. | Diagnostic logs include correlation ID, pipeline stage, retrieval counts, timing and error class; API keys and sensitive profile values are excluded or minimised. |

## 7. Non-functional requirements

| ID | Priority | Requirement | Proposed acceptance criterion |
|---|---:|---|---|
| NFR-001 | P0 | The enhanced source, index, PDF collection, manifest, logs and environment configuration shall be isolated from the original `guru_ai`. | Automated/manual path checks confirm no enhanced process reads or writes baseline `guru_ai/data` or `guru_ai/storage`. |
| NFR-002 | P0 | The enhanced project shall use the existing `GenAICourse/venv312` by default; no new virtual environment shall be created without explicit approval. | Setup documentation activates `../venv312`; no `.venv` creation instructions or committed venv are included. |
| NFR-003 | P0 | The enhanced UI shall target WCAG 2.2 AA contrast requirements for text and controls where applicable. | Contrast tests/documented spot checks meet 4.5:1 for normal text and 3:1 for large text and relevant non-text UI boundaries/focus indicators. |
| NFR-004 | P0 | The UI shall remain usable with keyboard navigation and visible focus states. | Keyboard-only acceptance cases pass for navigation, dropdowns, chat, buttons and upload controls where supported. |
| NFR-005 | P1 | The retrieval and reranking components shall be configurable and benchmarkable on the target Intel Mac environment. | The selected model and configuration meet agreed quality, latency and memory limits on the target device. |
| NFR-006 | P1 | The pipeline shall be reproducible for a fixed document corpus, configuration and model version where the underlying providers permit. | Dataset, source-document manifest, model/config versions and evaluation output are recorded. |
| NFR-007 | P1 | The system shall surface controlled errors for unavailable embedding/chat services, empty indexes, failed rewrite/reranking and malformed documents. | Failure-mode tests show a helpful user message and diagnostic correlation ID without exposing secrets. |
| NFR-008 | P1 | The application shall not represent retrieval scores as correctness probabilities. | UI/API schema and help text do not call raw similarity distances “confidence %”. |
| NFR-009 | P1 | The application shall not guarantee scheme eligibility, payments, subsidy approval or official application outcome. | All relevant answer and eligibility surfaces preserve the government-decision disclaimer. |
| NFR-010 | P1 | Dependencies shall be declared and tested against the shared Python 3.12 environment before implementation release. | A recorded `pip check`, import test and automated test run pass in `venv312`; dependency changes are reviewed. |

## 8. Out of scope for this increment

- OCR and table extraction from scanned PDFs.
- Scheme-version lifecycle management and automatic updates.
- Deterministic eligibility rules engine.
- Persistent multi-device chat history.
- User authentication and role-based access control.
- Voice input/output.
- Automatic government-site crawling, application submission or benefit tracking.
- Public cloud production deployment.

## 9. Open decisions requiring product-owner review

1. Final numerical thresholds for Recall@K, MRR/nDCG, citation precision, abstention and latency.
2. Evaluation dataset size and languages to be fully human-reviewed in the first increment.
3. Reranker model choice after quality/latency/memory benchmarking on the Intel Mac.
4. Whether a custom Streamlit component is permitted for dropdown consistency if native select styling cannot meet the requirement across browsers.
5. The exact supported viewport/browser matrix.
6. Whether evaluation reports should be generated as Markdown, JSON, CSV or all three.

## 10. Approval rule

The product owner must approve this FRD and the acceptance criteria before any source code or dependency file is changed. Requests to add or remove scope must be recorded in a change request and reflected in the RTM.
