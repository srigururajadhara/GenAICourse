FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libgomp1 tesseract-ocr tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY evals ./evals
COPY docs ./docs
COPY sample_documents_spotify_web_app_architecture.pdf ./sample_documents_spotify_web_app_architecture.pdf
RUN mkdir -p /app/storage
EXPOSE 8001 8502
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
