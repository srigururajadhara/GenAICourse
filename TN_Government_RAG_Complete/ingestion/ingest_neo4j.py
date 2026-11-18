import hashlib
import os
import re
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingestion.common import ROOT, RAW_HTML, RAW_PDF, META, load_json, save_json
from rag.embeddings import embed_documents, EMBEDDING_DIMENSIONS
from database.neo4j_connection import get_driver, get_database

LABEL = "TNSchemeChunk"
INDEX = "tn_scheme_chunk_embedding"
RELATIONSHIP = "TN_SCHEME_HAS_CHUNK"


def read_documents():
    documents = []
    for path in sorted(RAW_HTML.glob("*.json")):
        record = load_json(path, {})
        text = (record.get("text") or "").strip()
        if text:
            documents.append({
                "text": text, "title": record.get("title") or path.stem,
                "url": record.get("url") or "", "source_type": "html"
            })

    crawl_report = load_json(META / "crawl_report.json", {})
    pdf_url_by_path = {
        item.get("path"): item.get("url")
        for item in crawl_report.get("pdf_records", [])
    }
    for path in sorted(RAW_PDF.glob("*.pdf")):
        try:
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
            if text:
                documents.append({
                    "text": text, "title": path.name,
                    "url": pdf_url_by_path.get(str(path.relative_to(ROOT)), ""),
                    "source_type": "pdf"
                })
        except Exception as exc:
            print(f"[PDF EXTRACTION FAILED] {path.name}: {exc}")
    return documents


def stable_id(url, chunk_index, text):
    raw = f"{url}|{chunk_index}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main():
    docs = read_documents()
    if not docs:
        raise RuntimeError("No HTML/PDF text found. Run crawler first and inspect crawl_report.json.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=850, chunk_overlap=120,
        separators=["\n\n", "\n", "।", ". ", " ", ""]
    )
    chunks = []
    for doc in docs:
        for idx, chunk_text in enumerate(splitter.split_text(doc["text"])):
            if len(chunk_text.strip()) < 40:
                continue
            chunks.append({
                "chunk_id": stable_id(doc["url"], idx, chunk_text),
                "text": chunk_text,
                "title": doc["title"],
                "source_url": doc["url"],
                "source_type": doc["source_type"]
            })

    if not chunks:
        raise RuntimeError("Document extraction completed but no usable chunks were produced.")

    print(f"Embedding {len(chunks)} chunks locally...")
    vectors = embed_documents([item["text"] for item in chunks])
    if len(vectors) != len(chunks) or any(len(v) != EMBEDDING_DIMENSIONS for v in vectors):
        raise RuntimeError("Embedding output count/dimension validation failed.")

    driver = get_driver()
    try:
        with driver.session(database=get_database()) as session:
            session.run(f"""
                CREATE CONSTRAINT tn_scheme_chunk_id IF NOT EXISTS
                FOR (n:{LABEL}) REQUIRE n.chunk_id IS UNIQUE
            """).consume()

            # Dedicated project index; does not touch existing generic indexes.
            session.run(f"""
                CREATE VECTOR INDEX {INDEX} IF NOT EXISTS
                FOR (n:{LABEL}) ON (n.embedding)
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {EMBEDDING_DIMENSIONS},
                        `vector.similarity_function`: 'cosine'
                    }}
                }}
            """).consume()

            batch_size = 32
            for start in range(0, len(chunks), batch_size):
                batch = []
                for item, vector in zip(
                    chunks[start:start + batch_size],
                    vectors[start:start + batch_size]
                ):
                    item = dict(item)
                    item["embedding"] = vector
                    item["source_id"] = hashlib.sha256(
                        item["source_url"].encode("utf-8")
                    ).hexdigest()
                    batch.append(item)

                session.run(f"""
                    UNWIND $rows AS row
                    MERGE (s:TNSource {{source_id: row.source_id}})
                    SET s.url = row.source_url,
                        s.title = row.title,
                        s.source_type = row.source_type
                    MERGE (c:{LABEL} {{chunk_id: row.chunk_id}})
                    SET c.text = row.text,
                        c.title = row.title,
                        c.source_url = row.source_url,
                        c.source_type = row.source_type,
                        c.embedding = row.embedding,
                        c.updated_at = datetime()
                    MERGE (s)-[:{RELATIONSHIP}]->(c)
                """, rows=batch).consume()
                print(f"Stored {min(start + batch_size, len(chunks))}/{len(chunks)} chunks")

            counts = session.run(f"""
                MATCH (c:{LABEL}) RETURN count(c) AS chunks
            """).single()["chunks"]
    finally:
        driver.close()

    report = {
        "documents": len(docs),
        "chunks_processed": len(chunks),
        "neo4j_chunks_total": counts,
        "embedding_model": "intfloat/multilingual-e5-large",
        "embedding_dimensions": EMBEDDING_DIMENSIONS,
        "neo4j_label": LABEL,
        "vector_index": INDEX
    }
    save_json(META / "ingestion_report.json", report)
    print("Ingestion complete:", report)


if __name__ == "__main__":
    main()
