# Local validation guide

## 1. Review dependency impact first

```bash
cd ~/GenAICourse/pdf_intelligence_assistant_project
source ../venv312/bin/activate
python --version
python -m pip check
python -m pip install --dry-run -r requirements.txt
```

Do not run a real install until the dry-run is reviewed. The environment is shared with other projects.

## 2. Configure credentials

```bash
cp .env.example .env
```

Add the OpenAI key and Neo4j connection details. Do not commit `.env`.

## 3. Start services

Preferred local validation path:

```bash
docker compose up --build -d
docker compose ps
```

Check API liveness:

```bash
curl http://localhost:8001/health/live
curl http://localhost:8001/health/ready
```

UI: `http://localhost:8502`

## 4. Ingest sample document

Upload `sample_documents_spotify_web_app_architecture.pdf` through the UI. Refresh status until:

- overall status: `READY`
- vector pipeline: `READY`
- graph pipeline: `READY`

If the document enters `EXTRACTION_REVIEW_REQUIRED`, inspect the page-linked extracted passages in the UI. This occurs when OCR-derived text or low native-text yield is detected. Confirm the extraction is usable, explicitly approve it, and then wait for both indexes to finish. If any pipeline fails, inspect the safe warning shown in the UI and API logs. Do not enable Q&A for a partial index.

## 5. Test expected outcomes

Answerable:
- Which frontend technologies are listed?
- What does the Playback & Session Service manage?
- What are the roles of PostgreSQL and Redis according to this PDF?
- What does the recommendation service use to compute recommendations?

Unanswerable:
- What is the CEO's salary?
- What is Spotify's actual internal cloud topology?
- What are the credentials for the database?

The application must abstain on unsupported questions.

## 6. Run tests and golden set

```bash
pytest -q
python -m compileall -q app tests scripts
export EVAL_DOCUMENT_ID="<document-id>"
python scripts/run_golden_eval.py
```

Review each failure manually; the script is a lightweight smoke evaluation only.

## 7. Capture validation evidence

Record Python and dependency versions, commit hash, environment (without secrets), sample PDF hash, ingestion status, vector/graph counts, evaluation dataset version, test output, provider/model identifiers, latency and any failures. Do not include API keys, raw confidential PDF content or other users' documents in evidence artifacts.
