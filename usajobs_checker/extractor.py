"""Text and metadata extraction from resume files."""

import os
from pathlib import Path
from typing import Any

import pdfplumber
from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_MB = 5.0


class ExtractionError(Exception):
    """Raised when a resume file cannot be read or parsed."""


def get_file_metadata(path: Path) -> dict[str, Any]:
    """Return basic file metadata. Raises ExtractionError on problems."""
    if not path.exists():
        raise ExtractionError(f"File not found: {path}")
    if not path.is_file():
        raise ExtractionError(f"Not a file: {path}")

    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    suffix = path.suffix.lower()

    return {
        "path": str(path),
        "filename": path.name,
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 3),
        "extension": suffix,
        "size_ok": size_mb <= MAX_FILE_SIZE_MB,
        "format_ok": suffix in SUPPORTED_EXTENSIONS,
    }


def extract_pdf(path: Path) -> dict[str, Any]:
    """Extract text and page count from a PDF using pdfplumber."""
    try:
        with pdfplumber.open(path) as pdf:
            page_count = len(pdf.pages)
            texts = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                texts.append(text)
            full_text = "\n".join(texts).strip()
            return {
                "page_count": page_count,
                "page_count_reliable": True,
                "text": full_text,
                "text_length": len(full_text),
            }
    except Exception as exc:
        raise ExtractionError(f"Failed to parse PDF: {exc}") from exc


def extract_docx(path: Path) -> dict[str, Any]:
    """Extract text from a DOCX. Page count is estimated (not reliable)."""
    try:
        doc = Document(path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)
        # Rough estimate: ~500-600 words per page, ~5 chars per word average
        # Prefer recommending PDF for accurate page check
        char_count = len(full_text)
        estimated_pages = max(1, round(char_count / 3000))  # conservative estimate
        return {
            "page_count": estimated_pages,
            "page_count_reliable": False,
            "text": full_text.strip(),
            "text_length": char_count,
        }
    except Exception as exc:
        raise ExtractionError(f"Failed to parse DOCX: {exc}") from exc


def extract_resume(file_path: str | Path) -> dict[str, Any]:
    """
    Extract metadata and full text from a resume file.

    Returns a dict with keys: metadata, page_count, page_count_reliable, text, text_length.
    Raises ExtractionError on failure.
    """
    path = Path(file_path)
    metadata = get_file_metadata(path)

    if not metadata["format_ok"]:
        raise ExtractionError(
            f"Unsupported format '{metadata['extension']}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if metadata["extension"] == ".pdf":
        content = extract_pdf(path)
    elif metadata["extension"] == ".docx":
        content = extract_docx(path)
    else:
        raise ExtractionError("Unexpected extension after format check")

    return {
        "metadata": metadata,
        **content,
    }
