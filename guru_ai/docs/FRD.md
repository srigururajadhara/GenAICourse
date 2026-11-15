# Guru — Functional Requirements Document (FRD)

**Status:** Draft baseline  
**Version:** 0.1  
**Date:** 15 November 2026

## 1. Purpose

This document defines the functional and non-functional requirements for the current Guru baseline. Requirements are uniquely identified so they can be traced to implementation components and tests in `RTM.md`.

## 2. Product overview

Guru is a Streamlit + FastAPI application that answers questions using uploaded agricultural government scheme PDFs. It extracts page text, splits it into chunks, creates embeddings, stores them in a FAISS index, retrieves similar chunks and asks GPT-4o-mini to formulate a source-grounded answer.

## 3. User roles

| Role | Current capability | Limitations |
|---|---|---|
| End user / farmer | Ask questions, select profile fields and answer language, view citations | No account or personal data persistence |
| Knowledge-base contributor | Upload PDFs and rebuild the index through the UI | No role-based authorization or approval workflow |
| Administrator | No separate administrator role in baseline | Admin controls and audit are not implemented |

## 4. Functional requirements

Priority legend: **P1** = core baseline; **P2** = useful supporting baseline.

| ID | Requirement | Priority | Baseline status |
|---|---|---:|---|
| FR-001 | The system shall provide a web-based Streamlit dashboard for Guru. | P1 | Implemented |
| FR-002 | The system shall accept one or more PDF files through the user interface. | P1 | Implemented |
| FR-003 | The system shall apply a 30 MB per-file upload limit through the API. | P1 | Implemented |
| FR-004 | The system shall extract machine-readable text from PDF pages and retain page metadata. | P1 | Implemented; scanned-image pages are not OCR-supported |
| FR-005 | The system shall split extracted text into overlapping chunks using configured chunk size and overlap. | P1 | Implemented |
| FR-006 | The system shall attach source filename, state and category metadata to indexed chunks. | P1 | Implemented |
| FR-007 | The system shall generate embeddings using the configured OpenAI embedding model. | P1 | Implemented |
| FR-008 | The system shall persist and load a local FAISS vector index. | P1 | Implemented |
| FR-009 | The system shall retrieve up to the configured TOP_K semantically similar chunks for a question. | P1 | Implemented |
| FR-010 | The system shall use GPT-4o-mini (configurable) to generate an answer from retrieved evidence. | P1 | Implemented |
| FR-011 | The system shall instruct the model not to invent information missing from retrieved documents. | P1 | Implemented as prompt guidance; not independently guaranteed |
| FR-012 | The system shall display source filename, page number, state and excerpt for retrieved passages. | P1 | Implemented |
| FR-013 | The system shall allow the user to select English, Tamil, Hindi, Kannada, Telugu or Malayalam for the answer. | P1 | Implemented; language quality requires evaluation |
| FR-014 | The system shall collect optional farmer context including state, district, farmer type, land size, social category, crop and irrigation. | P1 | Implemented |
| FR-015 | The system shall pass recent chat turns to the answer-generation prompt for conversational context. | P1 | Implemented for active session; durable history not implemented |
| FR-016 | The system shall provide a preliminary scheme-fit/eligibility guidance interaction using the farmer profile and retrieved documents. | P1 | Implemented as AI-assisted text assessment; not a deterministic rules engine |
| FR-017 | The system shall show knowledge-base counts and uploaded-document metadata. | P2 | Implemented |
| FR-018 | The system shall expose health, knowledge-base, ingest and query API endpoints. | P1 | Implemented |
| FR-019 | The system shall allow the user to clear the active chat conversation. | P2 | Implemented |

## 5. Non-functional requirements

| ID | Requirement | Priority | Baseline status |
|---|---|---:|---|
| NFR-001 | API keys shall be read from environment configuration and not hard-coded in application source. | P1 | Implemented via `.env` / `.env.example`; deployment secret handling still required |
| NFR-002 | The UI shall clearly distinguish source-backed facts from missing or unverified information. | P1 | Partially implemented through prompt and citations; needs answer-quality tests |
| NFR-003 | The application shall provide user-friendly error messages when the API is unavailable or indexing fails. | P2 | Partially implemented |
| NFR-004 | The application shall preserve source page metadata through extraction, chunking and citations. | P1 | Implemented for text-extractable PDFs |
| NFR-005 | The system shall avoid presenting preliminary eligibility guidance as an official decision. | P1 | Implemented via UI and prompt disclaimers; needs regression tests |
| NFR-006 | The codebase shall include automated tests for core workflows. | P1 | Not sufficiently covered; only filename helper tests are currently present |
| NFR-007 | The service shall enforce authentication, authorization, rate limits and audit logging before public production deployment. | P1 | Not implemented |
| NFR-008 | The system shall support privacy-aware retention and deletion of user profile/chat data before public deployment. | P1 | Not implemented; chat is session-only in current UI |

## 6. Current constraints and known limitations

1. PDF ingestion uses text extraction; image-only/scanned pages may fail to yield usable content.
2. Retrieval uses FAISS semantic similarity only; no BM25 hybrid retrieval or reranking is present.
3. The current query path retrieves using the latest question; conversational follow-up query rewriting is not implemented.
4. State preference is applied after the initial top-K retrieval, so relevant state-specific passages outside that initial set may not be considered.
5. The preliminary eligibility feature is an LLM prompt-based comparison, not a validated rules engine.
6. Chat is held in Streamlit session state; it is not saved to a database across restarts or devices.
7. There is no user login, admin authorization or access-control layer on document upload/query endpoints.
8. There is no formal retrieval/answer evaluation dataset or automated groundedness gate.
9. Scheme documents can become outdated; metadata currently does not enforce effective-from/effective-to dates or supersession rules.
10. The application does not submit applications, confirm benefits, or provide official government decisions.

## 7. Acceptance approach

Each requirement must be linked to at least one verification case in `RTM.md`. Proposed enhancements must receive a new requirement ID and approval before implementation. The current baseline should not be treated as production-ready until the applicable P1 security, privacy, evaluation and operational requirements have been verified.
