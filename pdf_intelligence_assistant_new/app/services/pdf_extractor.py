from __future__ import annotations

import hashlib
import re
from io import BytesIO
from dataclasses import asdict, dataclass
from pathlib import Path

import fitz

from app.core.config import settings


@dataclass(frozen=True)
class PageBlock:
    document_id: str
    page_number: int
    block_order: int
    block_type: str
    text: str
    extraction_method: str = "native_text"
    section_path: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for piece in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(piece)
    return digest.hexdigest()


def extract_pdf(path: Path, document_id: str, max_pages: int) -> tuple[list[PageBlock], int, list[str]]:
    """Extract page-aware text blocks, with optional OCR for low-text pages."""
    warnings: list[str] = []
    blocks: list[PageBlock] = []
    try:
        pdf = fitz.open(path)
    except Exception as exc:
        raise ValueError("The PDF is corrupt, malformed or cannot be opened") from exc
    with pdf:
        if pdf.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported in this release")
        page_count = len(pdf)
        if page_count < 1:
            raise ValueError("The uploaded PDF has no pages")
        if page_count > max_pages:
            raise ValueError(f"PDF has {page_count} pages; configured maximum is {max_pages}")
        current_heading = ""
        for page_index, page in enumerate(pdf, start=1):
            try:
                raw_blocks = page.get_text("blocks", sort=True)
            except Exception as exc:
                warnings.append(f"Page {page_index}: text extraction failed ({type(exc).__name__})")
                raw_blocks = []
            page_text_length = 0
            block_order = 0
            for raw in raw_blocks:
                raw_text = str(raw[4]).strip() if len(raw) > 4 else ""
                if not raw_text:
                    continue
                page_text_length += len(raw_text)
                lines = [line.rstrip() for line in raw_text.splitlines() if line.strip()]
                heading_indices: set[int] = set()
                skip_indices: set[int] = set()
                for line_index, line in enumerate(lines):
                    if line_index + 1 < len(lines) and re.fullmatch(r"[=\-_*~]{3,}", lines[line_index + 1].strip()):
                        heading_indices.add(line_index)
                        skip_indices.add(line_index + 1)
                    if re.match(r"^\d+(?:\.\d+)*[.)]?\s+.{3,}$", line.strip()):
                        heading_indices.add(line_index)
                    if re.match(r"^[A-Z]\.\s+.{3,}$", line.strip()):
                        heading_indices.add(line_index)
                    if re.match(r"^[A-Z][A-Za-z0-9 /&()_-]{1,45}:$", line.strip()):
                        heading_indices.add(line_index)
                paragraph_lines: list[str] = []

                def flush_paragraph() -> None:
                    nonlocal block_order
                    paragraph = "\n".join(paragraph_lines).strip()
                    if paragraph:
                        blocks.append(
                            PageBlock(
                                document_id=document_id,
                                page_number=page_index,
                                block_order=block_order,
                                block_type="paragraph",
                                text=paragraph,
                                section_path=current_heading,
                            )
                        )
                        block_order += 1
                    paragraph_lines.clear()

                for line_index, line in enumerate(lines):
                    if line_index in skip_indices or re.fullmatch(r"[=\-_*~]{3,}", line.strip()):
                        continue
                    if line_index in heading_indices:
                        flush_paragraph()
                        current_heading = line.strip()
                        blocks.append(
                            PageBlock(
                                document_id=document_id,
                                page_number=page_index,
                                block_order=block_order,
                                block_type="heading",
                                text=current_heading,
                                section_path=current_heading,
                            )
                        )
                        block_order += 1
                    else:
                        paragraph_lines.append(line)
                flush_paragraph()
            # Preserve table structure when PyMuPDF can detect it; extraction is optional by parser version.
            try:
                table_finder = page.find_tables()
                for table_index, table in enumerate(getattr(table_finder, "tables", [])):
                    rows = table.extract() or []
                    rendered_rows = [
                        " | ".join(str(cell or "").strip() for cell in row)
                        for row in rows if any(str(cell or "").strip() for cell in row)
                    ]
                    table_text = "\n".join(rendered_rows).strip()
                    if table_text:
                        blocks.append(
                            PageBlock(
                                document_id=document_id,
                                page_number=page_index,
                                block_order=block_order + table_index + 1,
                                block_type="table",
                                text=table_text,
                                section_path=current_heading,
                            )
                        )
            except Exception:
                # Table detection can be unsupported or noisy for a particular PDF page.
                warnings.append(f"Page {page_index}: table structure could not be detected")
            if page_text_length < 40:
                if settings.ocr_enabled:
                    try:
                        import pytesseract
                        from PIL import Image

                        pixmap = page.get_pixmap(dpi=220, alpha=False)
                        image = Image.open(BytesIO(pixmap.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(image, lang=settings.ocr_lang).strip()
                        if ocr_text:
                            blocks.append(
                                PageBlock(
                                    document_id=document_id,
                                    page_number=page_index,
                                    block_order=len(raw_blocks) + 1,
                                    block_type="paragraph",
                                    text=ocr_text,
                                    extraction_method="ocr_tesseract",
                                    section_path=current_heading,
                                )
                            )
                            warnings.append(f"Page {page_index}: OCR text extracted; verify recognition quality")
                        else:
                            warnings.append(f"Page {page_index}: OCR returned no text")
                    except Exception as exc:
                        warnings.append(f"Page {page_index}: OCR unavailable or failed ({type(exc).__name__})")
                else:
                    warnings.append(f"Page {page_index}: low native-text yield; scanned/image-only content may need OCR")
    if not blocks:
        raise ValueError("No selectable text was extracted. OCR is not enabled or available for this document.")
    return blocks, page_count, warnings
