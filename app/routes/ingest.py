# app/routes/ingest.py
import os
from pathlib import Path

import aiofiles
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas.ingest import IngestResponse
from app.services.ingest_service import create_pending_record, process_pdf_background, compute_sha256
from app.logger import get_logger

router = APIRouter(prefix="/ingest", tags=["ingest"]) 
logger = get_logger(__name__)

PDF_ROOT = Path("pdfs")
INCOMING = PDF_ROOT / "incoming"
INCOMING.mkdir(parents=True, exist_ok=True)


async def _save_stream_to_path(upload: UploadFile, dest: Path) -> int:
    CHUNK = 64 * 1024
    size = 0
    async with aiofiles.open(dest, "wb") as f:
        while True:
            chunk = await upload.read(CHUNK)
            if not chunk:
                break
            size += len(chunk)
            await f.write(chunk)
    return size


@router.post("/", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_pdf_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    class_name: int = Query(..., description="Class number (e.g., 8-12)"),
    subject: str = Query(..., description="Subject name (e.g., Science, Math)"),
    chapter: str = Query(..., description="Chapter name or number"),
    session: AsyncSession = Depends(get_async_session),
    max_words: int = Query(250, description="Max words per chunk"),
    overlap_words: int = Query(50, description="Overlap words between chunks"),
):
    logger.info(
        "Received ingest request: filename=%s content_type=%s class=%s subject=%s chapter=%s max_words=%s overlap_words=%s",
        getattr(file, "filename", "<unknown>"), getattr(file, "content_type", "<unknown>"),
        class_name, subject, chapter, max_words, overlap_words,
    )

    if file.content_type not in ("application/pdf", "application/octet-stream"):
        logger.warning("Rejected upload (invalid content type): filename=%s content_type=%s", file.filename, file.content_type)
        raise HTTPException(status_code=400, detail="Only PDF uploads are allowed")

    safe_name = os.path.basename(file.filename)
    local_path = INCOMING / safe_name
    logger.debug("Saving upload to %s (safe_name=%s)", local_path, safe_name)

    try:
        size = await _save_stream_to_path(file, local_path)
        logger.info("Saved uploaded file: path=%s size=%d bytes", local_path, size)
    except Exception:
        logger.exception("Failed to save uploaded file to %s", local_path)
        raise HTTPException(status_code=500, detail="Failed to save file")

    checksum = compute_sha256(local_path)
    logger.debug("Computed SHA256 for %s: %s", local_path, checksum)

    # create DB record using service
    pdf = await create_pending_record(
        session, safe_name, str(local_path), size, checksum,
        class_name=class_name, subject=subject, chapter=chapter
    )
    logger.info("Created pending PDF record: id=%s filename=%s class=%s subject=%s chapter=%s",
                pdf.id, pdf.filename, class_name, subject, chapter)

    # schedule background worker (service)
    background_tasks.add_task(
        process_pdf_background, pdf.id, str(local_path), safe_name,
        class_name=class_name, subject=subject, chapter=chapter,
        max_words=max_words, overlap_words=overlap_words
    )
    logger.info(
        "Scheduled background processing: id=%s path=%s class=%s subject=%s chapter=%s max_words=%s overlap_words=%s",
        pdf.id, local_path, class_name, subject, chapter, max_words, overlap_words,
    )

    response = IngestResponse(
        id=pdf.id, filename=pdf.filename, status=pdf.status.value,
        class_name=pdf.class_name, subject=pdf.subject, chapter=pdf.chapter,
        created_at=pdf.created_at
    )
    logger.debug("Responding with 202 Accepted for id=%s filename=%s", pdf.id, pdf.filename)
    return response