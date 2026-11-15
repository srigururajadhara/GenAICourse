# Guru — Test Plan

**Status:** Draft; test execution evidence pending.

## 1. Test objectives

Verify document ingestion, retrieval, grounded response generation, citations, chat context, profile handling, API validation, error handling and safety disclaimers.

## 2. Test levels

- Unit: filename sanitisation, metadata mapping, chunking, page numbering, request validation.
- Integration: PDF ingestion to FAISS; query to retrieval to answer schema; API endpoint behaviour.
- UI: chat flow, language selector, profile fields, source panel, knowledge-base display and clear-chat action.
- RAG quality: retrieval relevance, source support, refusal when evidence is missing, citation correctness and multi-turn follow-ups.
- Security: file validation, secret handling, API access control, upload abuse, prompt injection and data retention.

## 3. Minimum functional test scenarios

| Test ID | Scenario | Expected result |
|---|---|---|
| TC-001 | Launch app when API is online | Dashboard loads and shows API/index state |
| TC-002 | Upload a valid text PDF | PDF is saved and index build reports counts |
| TC-003 | Upload file over 30 MB | Request is rejected with HTTP 413 |
| TC-004 | Upload a scanned image-only PDF | Current baseline reports no extractable text; OCR is not expected |
| TC-005 | Ask a question found in PDF | Answer includes supported source markers and page references |
| TC-006 | Ask about a fact absent from all PDFs | Assistant states the knowledge base does not contain enough evidence |
| TC-007 | Ask in Tamil and select Tamil response | Response is in Tamil; factual claims remain source-grounded |
| TC-008 | Change farmer state/profile | Profile is passed as request context; no missing field is assumed |
| TC-009 | Ask a follow-up referring to prior answer | Recent turns are included in model context; retrieval limitation is recorded |
| TC-010 | Run eligibility guidance with missing profile data | Missing information is identified as requiring verification |
| TC-011 | Inspect source evidence panel | Source filename, page and excerpt correspond to retrieved chunks |
| TC-012 | Clear active conversation | Current session messages are removed |
| TC-013 | Stop FastAPI and use UI | UI reports service is unavailable without crashing |
| TC-014 | Run query without API key or index | API returns a clear service/configuration error |

## 4. RAG evaluation dataset (to be created)

Create a reviewed set of questions with expected source document, page/section, expected answer points, language, state and query type. Include:

- Exact factual questions (scheme amount, deadline, land limit).
- Eligibility conditions and missing-profile cases.
- Document checklist and application-process questions.
- State-specific versus central scheme questions.
- Multi-turn follow-ups.
- Out-of-corpus and ambiguous questions.
- Conflicting or outdated document cases.

Recommended metrics for later approval: Recall@K, Mean Reciprocal Rank (MRR), citation precision, groundedness review score, answer completeness, abstention quality, latency and cost per query.

## 5. Exit criteria

Release criteria and metric thresholds must be approved by the product owner. Do not mark a test Passed without recording the environment, test data, result and evidence.

## 6. Baseline test execution note

During documentation review, `python -m compileall -q guru_ai/api guru_ai/core guru_ai/app.py` completed successfully. The available pytest run did **not** collect tests in the inspection environment because `langchain_community` was not installed (`ModuleNotFoundError`). Install the dependencies from `requirements.txt` in the project's supported Python environment and rerun pytest before claiming a passing test suite. No end-to-end OpenAI-backed workflow was executed in this review.
