from app.services.chunking import build_chunks
from app.services.pdf_extractor import PageBlock


def test_chunks_keep_document_and_page_provenance():
    blocks = [
        PageBlock("doc-1", 2, 0, "heading", "BACKEND", section_path="BACKEND"),
        PageBlock("doc-1", 2, 1, "paragraph", "NestJS manages the service layer." * 10, section_path="BACKEND"),
    ]
    chunks = build_chunks(blocks, "doc-1", max_chars=80, overlap=10)
    assert len(chunks) > 1
    assert all(chunk.document_id == "doc-1" for chunk in chunks)
    assert all(chunk.page_start == chunk.page_end == 2 for chunk in chunks)
    assert all(chunk.section_path == "BACKEND" for chunk in chunks)
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)
