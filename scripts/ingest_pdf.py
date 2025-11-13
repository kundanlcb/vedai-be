# scripts/ingest_pdf.py
"""
CLI script to ingest a local PDF file directly (useful for dev or CI).
Usage:
    pipenv run python scripts/ingest_pdf.py /path/to/file.pdf
"""
import asyncio
import sys
from pathlib import Path

from app.utils.chunker import chunk_pdf
from app.db import AsyncSessionLocal

BATCH = 500


async def ingest(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print("File not found:", file_path)
        return 1

    chunks = list(chunk_pdf(str(path), source_file=path.name))
    if not chunks:
        print("No chunks produced for file:", file_path)
        return 1

    from app.crud.content import bulk_create_chunks

    async with AsyncSessionLocal() as session:
        for i in range(0, len(chunks), BATCH):
            batch = chunks[i : i + BATCH]
            await bulk_create_chunks(session, batch)
            print(f"Ingested batch {i // BATCH + 1} / {((len(chunks)-1) // BATCH)+1}")
    print("Ingestion complete:", file_path)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_pdf.py <pdf_path>")
        raise SystemExit(2)
    file_arg = sys.argv[1]
    raise SystemExit(asyncio.run(ingest(file_arg)))