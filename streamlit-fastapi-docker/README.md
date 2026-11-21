# Streamlit + FastAPI + Docker Compose

A beginner-friendly two-container application.

- Streamlit frontend: http://localhost:8501
- FastAPI backend: http://localhost:8000
- FastAPI Swagger docs: http://localhost:8000/docs

## Run in VS Code

1. Extract this folder.
2. Open the extracted folder in VS Code.
3. Start Docker Desktop and wait for Docker Engine to run.
4. Open a terminal in the project root (the folder containing docker-compose.yml).
5. Run:

```bash
docker compose up --build
```

Open http://localhost:8501 and add a student. The Streamlit app sends a POST request to FastAPI. The list is stored in backend memory for this demo, so it resets when the backend restarts.

## Useful commands

```bash
docker compose ps
docker compose logs -f
docker compose logs -f backend
docker compose down
docker compose up --build -d
```

## Important networking concept

Inside the frontend container, `localhost` means the frontend container itself. Compose provides DNS for service names, so the frontend calls `http://backend:8000`. Your Mac browser accesses Streamlit through the published port `localhost:8501`.

## Folder structure

```text
streamlit-fastapi-docker/
├── docker-compose.yml
├── .dockerignore
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py
```
