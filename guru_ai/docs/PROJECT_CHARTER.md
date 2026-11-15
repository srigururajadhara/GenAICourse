# Guru — Project Charter

**Document status:** Draft for review  
**Project version:** 0.1 (baseline source package)  
**Product owner:** To be confirmed  
**Prepared on:** 15 November 2026

## 1. Project purpose

Guru is an educational prototype of an AI-assisted information service for discovering and understanding Indian agricultural government schemes. It lets a user ask questions in a conversational interface and receives an answer grounded in scheme PDFs uploaded to the application's knowledge base.

## 2. Problem statement

Scheme details are distributed across central and state government notifications, guidelines, FAQs and application documents. Users may find it difficult to locate eligibility conditions, benefits, documents, application steps, dates and applicable regions. Guru aims to make the information easier to explore while retaining links to the source document and page used by the answer.

## 3. Objectives

- Provide conversational question answering over uploaded agricultural scheme PDFs.
- Reduce the effort needed to locate relevant paragraphs in long documents.
- Show source document and page evidence for answers.
- Use the selected language and farmer profile as answer context.
- Provide preliminary eligibility guidance without claiming to make official decisions.
- Demonstrate an end-to-end RAG architecture using Python, LangChain, FAISS, FastAPI, Streamlit and OpenAI models.

## 4. Intended users

- Farmers and farming households.
- Agriculture students and researchers.
- Agriculture extension workers and support staff.
- Project demonstrators and evaluators.

## 5. Scope of the current baseline

Included: PDF upload, text extraction, chunking, metadata tagging, OpenAI embeddings, FAISS indexing, similarity retrieval, GPT-4o-mini answer generation, chat UI, farmer profile fields, selectable response language, source/page citations, preliminary eligibility guidance, FastAPI endpoints and knowledge-base statistics.

Not included in the current baseline: official eligibility decisions, application submission, government portal integration, live scheme-status verification, automatic web crawling, scanned-PDF OCR, voice input/output, persistent user accounts or durable chat history, admin role management, production security controls, and validated performance/accuracy SLAs.

## 6. Success measures (to be baselined)

- Every factual scheme answer includes supporting source references or clearly reports that evidence is insufficient.
- Retrieval evaluation is measured on a reviewed question set using Recall@K and MRR.
- Answer grounding is reviewed against expected source passages.
- Source title and page references are correct in the agreed test set.
- API and UI tests pass for the supported workflow.
- No API secrets are committed to source control.

Targets and test-set size require product-owner approval before being treated as release criteria.

## 7. Assumptions and constraints

- Users or administrators provide lawful, current and official documents.
- The application uses an OpenAI API key and therefore requires internet connectivity and may incur API charges.
- The current index is local FAISS storage.
- The application is a prototype and is not an official Government of India or state-government service.
- Users must verify dates, benefit amounts and eligibility with the responsible government authority.

## 8. Dependencies

- OpenAI API availability and account quota.
- Python package compatibility for the target operating system and Python version.
- Quality and text-extractability of uploaded PDFs.
- Correct state/category metadata supplied during document upload.

## 9. Project governance

No feature proposed in `FEATURE_BACKLOG.md` is approved for implementation by virtue of appearing in this document. Each enhancement must have an agreed requirement, acceptance criteria, priority and explicit owner approval before development begins.

## 10. Reference and attribution

The initial project concept and baseline feature outline were informed by the reference project supplied by the user: [SSR85Creates — Agricultural Schemes RAG](https://github.com/SSR85Creates/Python-Assignments/tree/main/09_Agricultural_Schemes_RAG). The current Guru source package was prepared independently from the feature outline shared in the conversation; the original repository's source contents and licence could not be verified during preparation. Before reusing any original code, assets or documentation, inspect its `LICENSE` and comply with its terms. See `ATTRIBUTION.md`.
