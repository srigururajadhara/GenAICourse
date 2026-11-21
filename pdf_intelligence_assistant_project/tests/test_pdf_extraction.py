from pathlib import Path

from app.services.pdf_extractor import extract_pdf


def test_sample_pdf_extracts_page_aware_content():
    sample = Path(__file__).resolve().parents[1] / "sample_documents_spotify_web_app_architecture.pdf"
    blocks, page_count, warnings = extract_pdf(sample, "sample-doc", max_pages=50)
    assert page_count == 6
    assert blocks
    assert any("Next.js" in block.text for block in blocks)
    assert any(block.block_type == "heading" and "Tech Stack Overview" in block.text for block in blocks)
    assert all(block.page_number in range(1, 7) for block in blocks)
