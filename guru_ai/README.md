# 🌾 Guru — Agricultural Government Scheme Assistant

A farmer-friendly Retrieval-Augmented Generation (RAG) application that answers questions from uploaded Indian Central and State Government agricultural scheme PDFs. Responses include source document names, page numbers and supporting text so users can verify what the assistant says.

> **Important:** This is an educational information assistant, not a government service. It does not submit applications or make official eligibility decisions. Upload current official documents and verify important decisions with the relevant department.

## What makes this version stronger?

- **Grounded answers:** The model is instructed to use retrieved document excerpts only and to say when the documents do not contain an answer.
- **Page-level evidence:** Every retrieved passage is shown with its PDF filename and page number; the response is encouraged to cite passages as `[S1]`, `[S2]`, etc.
- **Farmer profile context:** State, district, farmer type, landholding, social category, crop and irrigation details can be compared against explicit scheme conditions.
- **Multilingual interaction:** Ask and receive responses in English, Tamil, Hindi, Kannada, Telugu or Malayalam.
- **State-tagged knowledge base:** Tag each uploaded document as All India or a state and a scheme category. State-specific documents can be prioritised for a farmer profile.
- **Interactive Guru chat:** A dedicated chatbot interface supports ongoing conversations, remembers recent turns for follow-up questions during the active Streamlit session, and shows retrieved source passages and PDF page references below each answer. The backend accepts chat history as part of every query.
- **Separate backend and UI:** FastAPI provides ingestion, health, library and query endpoints; Streamlit provides the interactive dashboard.
- **Rebuildable local index:** PDFs are kept in `data/pdfs/`; FAISS is rebuilt from the local collection when new PDFs are ingested.

## Architecture

```text
Official agricultural scheme PDFs
              │
              ▼
        FastAPI ingestion
              │
       PyPDF page extraction
              │
    Metadata + page preservation
              │
   Recursive text chunking
              │
      OpenAI embeddings
              │
        FAISS vector index
              │
Farmer question + profile + language
              │
       Similarity retrieval
              │
   GPT-4o-mini grounded generation
              │
 Answer + source IDs + page citations
              │
       Streamlit dashboard
```

## Project structure

```text
guru_ai/
├── app.py                  # Streamlit UI
├── api/
│   └── main.py             # FastAPI endpoints
├── core/
│   ├── config.py           # Environment and paths
│   ├── ingestion.py        # PDF extraction, chunking and FAISS build
│   ├── rag.py              # Retrieval and grounded answer generation
│   └── schemas.py          # API request/response models
├── data/pdfs/              # Put official PDF files here (or upload in UI)
├── storage/                # Local FAISS index and manifest
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```


## Project documentation

The `docs/` folder contains the project charter, Functional Requirements Document (FRD), Requirements Traceability Matrix (RTM), architecture overview, test plan, proposed enhancement backlog, change-request template, approval workflow, attribution notes and release checklist. Proposed enhancements are **not approved for implementation** until the project owner explicitly approves their requirements.

- [Project Charter](docs/PROJECT_CHARTER.md)
- [Functional Requirements Document (FRD)](docs/FRD.md)
- [Requirements Traceability Matrix (RTM)](docs/RTM.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [LangChain 1.x setup using the existing venv312](docs/LANGCHAIN_1X_SETUP.md)
- [Test Plan](docs/TEST_PLAN.md)
- [Proposed Feature Backlog](docs/FEATURE_BACKLOG.md)
- [Change Request Template](docs/CHANGE_REQUEST_TEMPLATE.md)
- [Approval Workflow](docs/APPROVAL_WORKFLOW.md)
- [Attribution and Licence Notes](docs/ATTRIBUTION.md)
- [Release Checklist](docs/RELEASE_CHECKLIST.md)

## Requirements

- Python 3.11 or 3.12
- An OpenAI API key with API billing enabled
- Internet connectivity for OpenAI embeddings and answer generation
- Official scheme PDFs (Central and/or State Government)

> **Mac note:** On an Intel Mac, use a Python 3.11/3.12 virtual environment. If `faiss-cpu` does not install on your macOS/Python combination, use a compatible wheel/Conda environment or ask to switch the vector-store adapter; the rest of the application is not tied to a specific operating system.

## Setup on macOS (reuse your existing `venv312`)

This project is designed to use the shared Python 3.12 environment already present at `~/GenAICourse/venv312`. **Do not create another virtual environment.**

From a VS Code terminal:

```bash
cd ~/GenAICourse
source venv312/bin/activate
python -m pip freeze > ~/GenAICourse/venv312-before-guru-upgrade.txt
cd guru_ai
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip check
```

The requirements use a coordinated LangChain 1.x package set to avoid mixing `langchain-core` 0.3.x with LangGraph/Hugging Face packages that require Core 1.x. Some older training notebooks that import legacy chains from `langchain.chains` may need `langchain_classic.chains` after upgrading to LangChain v1; see the official migration guide. The current Guru code uses `langchain-core`, `langchain-openai`, `langchain-text-splitters`, and the `langchain-community` PDF/FAISS adapters.

**Maintenance note:** the LangChain maintainers archived `langchain-community` in June 2026. Guru currently uses `PyPDFLoader` and FAISS from that package, so this is a known dependency risk in the baseline. We should plan a separate approved migration to maintained integrations or application-owned adapters; it is not silently included in this dependency alignment.

Create your environment file if it does not already exist:

```bash
cp .env.example .env
```

Open `.env` and replace `your_openai_api_key_here` with your API key. Do not commit `.env` or share it publicly.

## Add your scheme knowledge base

1. Open the Streamlit app.
2. In the left sidebar, upload one or more official PDF documents.
3. Tag them as **All India** or the applicable state and select a document category.
4. Click **Build / Refresh Knowledge Base**.
5. Wait for the page count and indexed chunk count to appear in the dashboard.
6. Open **Ask Guru** and start chatting in the language you prefer. Ask follow-up questions naturally; recent messages are included as conversation context, and each answer includes expandable source/page evidence. Use **Clear conversation** to reset the current chat.

You can also copy PDFs directly into `data/pdfs/` and call the ingestion endpoint by uploading them through the interface. The index is rebuilt from the PDF directory whenever new files are ingested.

## Example questions

- What are the benefits and eligibility criteria of PM-KISAN?
- What documents are required for crop insurance?
- Is there a subsidy for drip irrigation in Tamil Nadu?
- What is the application process and where should I apply?
- Compare the eligibility conditions in these two uploaded scheme guidelines.
- இந்தத் திட்டத்தின் மூலம் விவசாயிகளுக்கு என்ன நன்மைகள் கிடைக்கும்?
- ನನ್ನ ರಾಜ್ಯದಲ್ಲಿ ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳ ಸಹಾಯಧನಕ್ಕೆ ಅರ್ಹತೆ என்ன?

The answer will be based only on the PDFs in your knowledge base. If a scheme document is missing or does not mention a requested detail, the assistant should say so.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | API and index status |
| `GET` | `/api/v1/knowledge-base` | Indexed PDF, page and chunk details |
| `POST` | `/api/v1/ingest` | Upload PDFs and rebuild FAISS |
| `POST` | `/api/v1/query` | Retrieve evidence and generate an answer |

## Evaluation checklist before demonstration

- [ ] Upload at least 3 official PDFs, including one state-specific guideline.
- [ ] Confirm page references against the original PDF.
- [ ] Ask questions whose answers are present in the PDFs.
- [ ] Ask a question whose answer is absent; confirm the assistant does not invent it.
- [ ] Test English and Tamil/Kannada/Hindi responses.
- [ ] Test an eligibility question with some missing farmer-profile fields.
- [ ] Add a revised PDF and rebuild the index.
- [ ] Compare generated answers against a human-verified answer set.

## Security and limitations

- Store API keys only in `.env`; never hard-code them or upload them to GitHub.
- Uploaded PDFs and the FAISS index are stored locally and excluded from Git by default.
- The current version extracts text-based PDFs. Scanned/image-only PDFs need an OCR enhancement.
- The app does not crawl government websites automatically. Upload the latest official circulars and guidelines yourself.
- A retrieved passage and a generated answer can still be incomplete or misinterpreted. Always inspect the source page.
- The profile is request context and is not stored in a user account or database by this application.

## Future enhancements

1. OCR for scanned PDFs and tables.
2. Hybrid BM25 + FAISS retrieval and cross-encoder reranking.
3. Automated evaluation using a hand-verified question/answer benchmark and RAGAS.
4. Speech input/output for farmer accessibility.
5. Official portal links and application workflow references extracted from trusted documents.
6. Admin authentication, document versioning and audit logs for multi-user deployment.
7. Docker deployment and cloud-hosted vector database for a team setup.

## License

For educational and demonstration use. Respect the copyright and terms of use of every uploaded government or third-party document.
