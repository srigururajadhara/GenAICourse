# Guru — Requirements Traceability Matrix (RTM)

**Status:** Draft baseline traceability  
**Version:** 0.1  
**Date:** 15 November 2026

The RTM maps each FRD requirement to its implementation location and verification coverage. A component being present in source code does not mean it has passed end-to-end validation.

| Requirement ID | Implementation reference | Verification ID | Verification description | Current status |
|---|---|---|---|---|
| FR-001 | `app.py` | TC-001 | Launch Streamlit and verify dashboard tabs render | Not yet evidenced by automated UI test |
| FR-002 | `app.py`, `api/main.py` | TC-002 | Upload a valid PDF through the UI/API | Not yet evidenced by integration test |
| FR-003 | `api/main.py` | TC-003 | Upload a PDF larger than 30 MB and verify HTTP 413 | Not yet automated |
| FR-004 | `core/ingestion.py` | TC-004 | Extract text from a multi-page text PDF and verify page metadata | Not yet automated |
| FR-005 | `core/ingestion.py` | TC-005 | Verify chunk size/overlap behaviour and chunk metadata | Not yet automated |
| FR-006 | `core/ingestion.py` | TC-006 | Verify source/state/category metadata survives indexing | Not yet automated |
| FR-007 | `core/ingestion.py` | TC-007 | Build embeddings with a configured OpenAI key | Requires live API test |
| FR-008 | `core/ingestion.py` | TC-008 | Save and reload FAISS index, then retrieve a known passage | Not yet automated |
| FR-009 | `core/rag.py` | TC-009 | Query a known corpus and inspect retrieved passages | Not yet automated |
| FR-010 | `core/rag.py` | TC-010 | Verify the configured chat model is invoked and answer returned | Requires live API test |
| FR-011 | `core/rag.py` | TC-011 | Ask a question absent from corpus and verify insufficient-evidence response | Not yet automated |
| FR-012 | `core/rag.py`, `app.py` | TC-012 | Verify filename and 1-based page reference in evidence panel | Not yet automated |
| FR-013 | `app.py`, `core/rag.py` | TC-013 | Run a representative query in each of six selected languages and review quality | Not yet evaluated |
| FR-014 | `app.py`, `core/schemas.py` | TC-014 | Enter profile fields and verify request payload | Not yet automated |
| FR-015 | `app.py`, `core/rag.py` | TC-015 | Ask a follow-up question and verify previous turns are included in prompt | Not yet automated |
| FR-016 | `app.py`, `core/rag.py` | TC-016 | Run eligibility guidance with matched, mismatched and missing profile fields | Not yet validated; prompt-based only |
| FR-017 | `core/ingestion.py`, `app.py` | TC-017 | Upload and index PDFs, then verify counts and metadata | Not yet automated |
| FR-018 | `api/main.py` | TC-018 | Exercise health, knowledge-base, ingest and query endpoints | Not yet automated |
| FR-019 | `app.py` | TC-019 | Clear chat and verify active messages are removed | Not yet automated |
| NFR-001 | `core/config.py`, `.env.example`, `.gitignore` | TC-020 | Confirm secret is read from environment and `.env` is ignored | Manual review required |
| NFR-002 | `core/rag.py`, `app.py` | TC-021 | Review answer for citations and insufficient-evidence behaviour | Not yet automated |
| NFR-005 | `core/rag.py`, `app.py` | TC-022 | Verify UI/prompt do not claim official eligibility approval | Not yet automated |
| NFR-006 | `tests/` | TC-023 | Run test suite and inspect requirement coverage | Incomplete; current tests cover filename sanitisation only; pytest collection was blocked in the inspection environment because `langchain_community` was missing |
| NFR-007 | API/security layer | TC-024 | Verify auth, authorization, rate limiting and audit trail | Not implemented — open gap |
| NFR-008 | persistence/privacy layer | TC-025 | Verify data retention, deletion and privacy controls | Not implemented — open gap |

## Coverage summary

- Functional requirements listed: 19
- Non-functional requirements listed: 8
- Requirements with implementation references: baseline functionality is mapped; some controls are explicitly identified as absent.
- Automated end-to-end requirement coverage: not established.
- Live OpenAI integration and multilingual quality: not verified in this documentation pass.

## RTM maintenance rules

1. Never delete an approved requirement ID; mark it Retired and record why.
2. Give every new requirement a unique ID.
3. Every approved requirement must map to an implementation component and at least one test case.
4. Update test status only after evidence is recorded.
5. A requirement change must be reviewed for impact on architecture, code, tests, README and user documentation.
