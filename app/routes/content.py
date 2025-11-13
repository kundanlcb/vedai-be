# app/routes/content.py
import os
from pathlib import Path
from typing import List

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.content import create_chunk, bulk_create_chunks, search_chunks_by_keyword
from app.db import AsyncSessionLocal
from app.schemas.content import ChunkCreate, ChunkRead
from app.utils.chunker import chunk_pdf

router = APIRouter(prefix="/content", tags=["content"])

# Uploads directory (dev)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _save_upload(file: UploadFile, destination: Path) -> Path:
    """
    Save uploaded file asynchronously to `destination`.
    Uses streaming writes to handle large files.
    Returns the saved Path.
    """
    CHUNK_SIZE = 1024 * 64
    async with aiofiles.open(destination, "wb") as out_file:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            await out_file.write(chunk)
    return destination


@router.post("/upload_pdf", response_model=dict)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF to the server (dev). Returns the saved file path.
    In production, swap this to upload directly to S3/MinIO and return an object key.
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        # some clients send application/octet-stream for pdfs
        raise HTTPException(status_code=400, detail="Only PDF uploads are allowed")

    safe_name = os.path.basename(file.filename)
    dest = UPLOAD_DIR / safe_name
    await _save_upload(file, dest)
    return {"filename": str(dest)}


@router.post("/ingest", response_model=dict)
async def ingest_pdf(
    background_tasks: BackgroundTasks,
    filename: str,
        max_words: int = Query(250, ge=50, le=2000),
    overlap_words: int = Query(50, ge=0, le=500),
):
    """
    Start ingestion of a previously uploaded PDF file.
    - `filename` should be a path returned by /content/upload_pdf (relative to project root) OR an absolute path.
    This endpoint schedules ingestion in the background and returns a task acknowledgment quickly.
    """
    path = Path(filename)
    if not path.exists():
        # try in uploads dir
        candidate = UPLOAD_DIR / path.name
        if candidate.exists():
            path = candidate
        else:
            raise HTTPException(status_code=404, detail="File not found")

    # run ingestion in background to avoid blocking the request
    background_tasks.add_task(_ingestion_task, str(path), str(path.name), max_words, overlap_words)
    return {"status": "ingestion_started", "file": str(path)}


async def _ingestion_task(file_path: str, source_file: str, max_words: int, overlap_words: int):
    """
    Background ingestion task. Creates its own DB session and performs bulk inserts.
    IMPORTANT: This function intentionally creates its own DB session rather than reusing
    the request session to avoid session scope issues in background tasks.
    """

    chunks = list(chunk_pdf(file_path, source_file=source_file, max_words=max_words, overlap_words=overlap_words))
    if not chunks:
        return

    # Use a fresh AsyncSession for background work
    async with AsyncSessionLocal() as session:
        # insert in batches to limit memory/transaction size
        BATCH = 500
        for i in range(0, len(chunks), BATCH):
            batch = chunks[i : i + BATCH]
            await bulk_create_chunks(session, batch)


@router.post("/chunks", response_model=ChunkRead)
async def create_chunk_endpoint(chunk_in: ChunkCreate, session: AsyncSession = Depends(AsyncSessionLocal)):
    """
    Single chunk create endpoint for debugging/admin use.
    """
    created = await create_chunk(session, chunk_in.dict())
    return created


@router.get("/search", response_model=List[ChunkRead])
async def search(q: str = Query(..., min_length=1), limit: int = Query(10, gt=0), session: AsyncSession = Depends(AsyncSessionLocal)):
    """
    Naive text search (SQL ILIKE). We'll later replace/augment this with vector retrieval.
    """
    results = await search_chunks_by_keyword(session, q, limit=limit)
    return results