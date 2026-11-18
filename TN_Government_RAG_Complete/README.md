# Tamil Nadu Government Schemes — Bilingual RAG Chatbot

A local Streamlit RAG application for searching Tamil Nadu Government scheme information in **Tamil and English**.

## What this project does

1. Discovers relevant same-domain pages from configured Tamil Nadu Government portal entry points.
2. Checks `robots.txt` before crawling.
3. Crawls HTML pages and downloads PDF files with bounded depth, page limits, timeouts and request delays.
4. Extracts visible HTML text and PDF text while preserving source URLs and crawl metadata.
5. Splits content into chunks and creates local multilingual embeddings using `intfloat/multilingual-e5-large` through FastEmbed.
6. Stores project-specific nodes and vectors in Neo4j AuraDB using a separate label and index.
7. Retrieves evidence and asks an OpenAI chat model to answer in the user's language, with source references.

## Important coverage limitation

This is a crawler and RAG application, **not a guarantee that every government scheme has been captured**. The official portal may link to other department domains, use JavaScript-rendered pages, block automated requests, or publish documents outside the configured domain. External domains are intentionally not followed by default. Review `data/metadata/discovery_report.json` and `data/metadata/crawl_report.json` after ingestion. Add separately verified official department sources to `config/sources.json` if broader coverage is required.

The chatbot must say when retrieved official material does not establish an answer. It must not infer that a scheme is currently active merely because an old page exists.

## Architecture

- UI: Streamlit
- Crawler: Requests + BeautifulSoup
- PDF text extraction: pypdf
- Embeddings: FastEmbed multilingual E5, 1,024 dimensions, local ONNX inference
- Vector store: Neo4j AuraDB vector index
- Answer generation: OpenAI chat model
- Language support: Tamil and English, with cross-language semantic retrieval

## Requirements

- Python 3.10–3.12 recommended
- Neo4j AuraDB instance with vector index support
- OpenAI API key for answer generation
- Internet access for crawling and initial model download

## Installation

Use a dedicated virtual environment if possible. If you choose to use an existing shared environment, avoid upgrading unrelated packages.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your own credentials. Do not share `.env` or paste passwords into chat. If a Neo4j password has previously been exposed, rotate it in Aura Console before using it.

## Run the pipeline

Run commands from the project root:

```bash
python -m ingestion.discover_sources
python -m ingestion.crawl_website
python -m ingestion.ingest_neo4j
```

The first embedding run downloads the multilingual model (about 2.2 GB). Subsequent runs reuse the local FastEmbed cache.

Start with conservative crawler limits. Inspect the reports before increasing `MAX_PAGES` or `MAX_DEPTH`.

## Run the chatbot

```bash
streamlit run app.py
```

## Neo4j isolation and safety

This project writes only to these project-specific labels and relationship types:

- `TNSchemeChunk`
- `TNSource`
- `TN_SCHEME_HAS_CHUNK`

It creates a dedicated vector index named `tn_scheme_chunk_embedding`. It does not delete, clear, or overwrite generic nodes or the existing `SchemeChunk` label/index used by another project. Do not rename these labels/indexes to generic names.

The ingestion script uses `MERGE` on stable chunk/source identifiers, so rerunning ingestion updates matching project records rather than creating duplicates.

## Operational checks

```bash
python -m compileall -q .
pytest -q
python -m ingestion.discover_sources
python -m ingestion.crawl_website
python -m ingestion.ingest_neo4j
```

A successful unit test run does not prove live website coverage, Aura connectivity, API quota, or answer quality. Those need to be tested in your environment.

## Known limitations / next hardening steps

- JavaScript-rendered content is not rendered by this Requests crawler.
- OCR is not included for scanned/image-only PDFs.
- External official department websites are not crawled unless explicitly added and the allowlist is extended after review.
- Scheme entities are indexed as evidence chunks; this version does not claim complete normalized extraction of every eligibility field or Government Order.
- Verify official documents and dates before using answers for eligibility or application decisions.
