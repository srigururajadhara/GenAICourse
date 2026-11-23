# Guru PDF Intelligence — refreshed UI and private Docker setup

This refresh keeps the existing FastAPI + Streamlit + hybrid RAG architecture and replaces the technical-looking Streamlit screen with a document workspace.

## Current user-facing capabilities

- Overview dashboard and recent documents
- PDF upload and document library search
- Processing status, extraction review/approval and retry
- Evidence-grounded chat with citations and retrieval-channel details
- Executive, detailed and section summaries with citation expanders
- Extracted passage browser with text filtering
- Document deletion remains available through the existing backend API; the current UI release intentionally avoids exposing a destructive action in the main navigation

The backend currently exposes single-document Q&A and summaries. Cross-document comparison, OCR language selection, direct PDF preview, persistent conversation history and end-user account management are not implemented by this UI refresh and require backend/API work.

## Local setup

1. Copy `.env.example` to `.env` and configure OpenAI and Neo4j AuraDB credentials.
2. For local development, leave `APP_ENV=development` and `API_KEYS_JSON=` empty; the existing development key is used. Do not use this development setting on a public server.
3. Install dependencies using your existing Python 3.12 environment: `pip install -r requirements.txt`.
4. Start API: `uvicorn app.api.main:app --host 0.0.0.0 --port 8001`.
5. In another terminal, start UI: `streamlit run app/ui/streamlit_app.py --server.port 8502`.
6. Open `http://localhost:8502`.

## Docker Compose

The included Compose file is private-by-default and uses the configured Neo4j AuraDB endpoint. It does not start a local Neo4j container and does not add a Traefik router. This avoids accidentally publishing an unauthenticated shared workspace.

For development, configure `.env` with:

```dotenv
APP_ENV=development
API_BASE_URL=http://api:8001
STORAGE_ROOT=/app/storage
SQLITE_PATH=/app/storage/app.db
NEO4J_URI=neo4j+s://YOUR_AURADB_INSTANCE.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YOUR_AURADB_PASSWORD
```

The `.env` file must also contain a valid `OPENAI_API_KEY`. Do not commit `.env`.

Validate and start:

```bash
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=80 api
```

Open locally on the VPS through an SSH tunnel from your Mac:

```bash
ssh -L 8502:127.0.0.1:8502 root@YOUR_VPS_IP
```

Then browse to `http://localhost:8502`.

## Production security gate

Do not attach the UI to a public Traefik router until real user authentication and per-user workspace provisioning/isolation are implemented and tested. The current API-key-to-workspace mapping is not an end-user login system. If several people share one API key/workspace, they share document access. The private loopback bindings in this Compose file are intentional.

For production `API_KEYS_JSON` must be a valid one-line JSON object mapping strong API keys (at least 32 characters) to workspace IDs, for example:

```dotenv
API_KEYS_JSON='{"REPLACE_WITH_LONG_RANDOM_KEY":"private-beta"}'
```

Never paste the real key into support chats or commit it to Git.
