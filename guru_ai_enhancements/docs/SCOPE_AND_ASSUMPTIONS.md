# Scope, Assumptions and Constraints

## Confirmed from user decisions

- The original `guru_ai` project must not be changed during enhancement development.
- New work belongs in `guru_ai_enhancements`.
- The existing `venv312` should be reused; the user does not want a new venv for each project.
- Guru should have an original, distinctive UI rather than repeat a generic/copycat design.
- Dropdown options must remain readable when the list is open; the supplied Irrigation menu screenshot demonstrates the defect.
- The user wants an approval-first process: requirements must be reviewed and confirmed before implementation.

## Baseline facts from reviewed project source snapshot

- Streamlit UI and FastAPI backend.
- PDF text extraction using `PyPDFLoader` and chunking with `RecursiveCharacterTextSplitter`.
- OpenAI embeddings, local FAISS vector store and GPT-4o-mini answer generation.
- Semantic search with configured top-K.
- Recent chat turns are included in answer generation, but no standalone follow-up query rewrite is present in the reviewed `core/rag.py`.
- Reranking, BM25, calibrated abstention and a formal evaluation runner are not present in the reviewed source.
- State filtering is applied after the initial semantic matches.

## Assumptions requiring validation during implementation planning

- The user's local working `guru_ai` has the most recent contrast-refresh UI file installed and is running successfully, as reported by the user. The local working directory is not directly mounted here, so exact source parity is not independently confirmed.
- The shared `venv312` is Python 3.12 and currently supports the user's course projects. Its package set must be checked before adding any new dependency.
- The first enhanced release remains a local Mac application.
- The user can provide permitted official PDF documents and review test answers/citations.

## Screenshot/source discrepancy to resolve

The latest supplied UI screenshot displays “Limit 200MB per file” in the uploader. The source snapshot reviewed for this pack enforces a 30 MB per-file limit in `api/main.py`. The actual running backend limit must be inspected before the enhanced project adopts an upload limit. Do not assume the UI label is authoritative or change the backend based only on the screenshot.

## Constraints

- Intel Mac hardware with 16 GB RAM is the target local test machine, based on previously supplied system information.
- No new virtual environment by default.
- No baseline data/index reuse.
- No official eligibility or application-submission claims.
- No external asset copied without licence/attribution review.
