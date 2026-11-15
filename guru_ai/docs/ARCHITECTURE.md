# Guru — Architecture Overview

## 1. Logical components

| Component | Technology | Responsibility |
|---|---|---|
| User interface | Streamlit | Chat, farmer profile, language selection, PDF upload, eligibility guidance and knowledge-base view |
| API layer | FastAPI | Health, ingestion, knowledge-base and query endpoints |
| PDF loader | LangChain PyPDFLoader / pypdf | Extract page text and page metadata |
| Text splitter | RecursiveCharacterTextSplitter | Split pages into overlapping chunks |
| Embedding service | OpenAI embeddings | Convert chunks and queries into vectors |
| Vector index | FAISS | Similarity search over document chunks |
| Answer model | OpenAI GPT-4o-mini by default | Compose response from retrieved evidence and request context |
| Local data | `data/pdfs`, `storage/` | Uploaded PDFs, FAISS files and document manifest |

## 2. Ingestion sequence

1. Contributor uploads PDF files and chooses a state and category.
2. API validates filename extension, non-empty content and per-file size.
3. Files are saved in `data/pdfs/` with a sanitised, non-overwriting filename.
4. Each readable PDF is loaded page by page.
5. Source filename, document ID, state and category are attached as metadata.
6. Page text is split into overlapping chunks.
7. OpenAI embeddings are generated.
8. FAISS index and a manifest are saved locally.

## 3. Query sequence

1. User enters a question and selects language/profile fields.
2. Streamlit sends question, recent conversation turns, selected language and farmer profile to FastAPI.
3. Backend loads the FAISS index and retrieves the configured top-K similar chunks.
4. State preference is applied to the initially retrieved matches when possible.
5. Retrieved excerpts and metadata are sent to GPT-4o-mini with system instructions.
6. Backend returns answer, evidence excerpts, source IDs, page references and suggested follow-up questions.
7. Streamlit renders the answer and expandable evidence panel.

## 4. API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Service and index status |
| GET | `/api/v1/knowledge-base` | Index counts and document metadata |
| POST | `/api/v1/ingest` | Upload PDFs and rebuild index |
| POST | `/api/v1/query` | Ask a source-grounded question |
| GET | `/docs` | FastAPI OpenAPI / Swagger UI during development |

## 5. Data locations

- Source PDFs: `data/pdfs/`
- FAISS index: `storage/faiss_index/`
- Document manifest: `storage/manifest.json`
- Credentials: local `.env` file (must not be committed)

## 6. Current architectural limitations

The baseline is a single local FAISS index. It does not yet provide hybrid lexical/semantic search, reranking, OCR, query rewriting for follow-up questions, date-aware scheme version selection, persistent user sessions, authentication, authorization, or production observability. These are candidate enhancements only; see `FEATURE_BACKLOG.md`.


## LangChain dependency generation

The baseline dependency set targets LangChain 1.x using `langchain-core`, `langchain-openai`, and `langchain-text-splitters`. The current PDF loader and FAISS adapter still come from `langchain-community` 0.4.2, which was archived by its maintainers in June 2026. Migrating these two integration points is a separate technical-debt item and must go through the project's change-approval workflow.
