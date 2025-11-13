# app/utils/chunker.py
import re
from typing import Generator, Dict, Any, Optional, List

import pdfplumber

# NOTE: this module performs synchronous PDF parsing because pdfplumber does not provide an async API.
# We keep it simple and CPU-light. For very large ingestion jobs, run in a worker process / Celery / background container.

_WORD_RE = re.compile(r"\S+")


def _word_count(text: str) -> int:
    return len(_WORD_RE.findall(text))


def chunk_text(
    text: str,
    max_words: int = 250,
    overlap_words: int = 50,
) -> List[str]:
    """
    Chunk text into overlapping windows by *words*.
    - `max_words`: target words per chunk (approx)
    - `overlap_words`: overlap between consecutive chunks

    Returns a list of chunk strings.
    """
    if not text:
        return []

    words = _WORD_RE.findall(text)
    if not words:
        return []

    chunks: List[str] = []
    i = 0
    n = len(words)
    while i < n:
        end = min(i + max_words, n)
        chunk = " ".join(words[i:end])
        chunks.append(chunk)
        if end == n:
            break
        i = end - overlap_words
        if i < 0:
            i = 0
    return chunks


def chunk_pdf(
    file_path: str,
    source_file: Optional[str] = None,
    class_name: Optional[int] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    max_words: int = 250,
    overlap_words: int = 50,
) -> Generator[Dict[str, Any], None, None]:
    """
    Open a PDF and yield chunk dicts suitable for `bulk_create_chunks`.
    Each yielded dict:
      {
        "source_file": <file name>,
        "class_name": <class number or None>,
        "subject": <subject name or None>,
        "chapter": <chapter name or None>,
        "page": <page number>,
        "text": <chunk text>,
        "is_example": False,
        "tokens": <approx words>
      }
    NOTE: pdfplumber.extract_text() returns text in reading order for many PDFs but can miss
    complex layouts. For scanned PDFs, OCR (Tesseract) is required prior to this step.
    """
    source_file = source_file or file_path
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if not text:
                continue
            page_chunks = chunk_text(text, max_words=max_words, overlap_words=overlap_words)
            for chunk in page_chunks:
                yield {
                    "source_file": source_file,
                    "class_name": class_name,
                    "subject": subject,
                    "chapter": chapter,
                    "page": page_num,
                    "text": chunk,
                    "is_example": False,
                    "tokens": _word_count(chunk),
                }