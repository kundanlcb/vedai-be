# app/services/ingest_service.py
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy import update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import AsyncSessionLocal
from app.models.ingest import PdfFile, PdfStatus
from app.services.rag import load_and_split_pdf, store_embeddings
from app.logger import get_logger

logger = get_logger(__name__)

PDF_ROOT = Path("pdfs")
INCOMING = PDF_ROOT / "incoming"
PROCESSING = PDF_ROOT / "processing"
PROCESSED = PDF_ROOT / "processed"
FAILED = PDF_ROOT / "failed"

for d in (INCOMING, PROCESSING, PROCESSED, FAILED):
    d.mkdir(parents=True, exist_ok=True)


def compute_sha256(path: Path) -> str:
    """Compute SHA256 checksum of file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


async def create_pending_record(
    session: AsyncSession,
    filename: str,
    filepath: str,
    filesize: int,
    checksum: Optional[str] = None,
    class_name: Optional[int] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
) -> PdfFile:
    """Create PdfFile record with PENDING status using naive UTC datetime."""
    # Use naive UTC datetimes for TIMESTAMP WITHOUT TIME ZONE columns
    now = datetime.utcnow()

    pdf = PdfFile(
        filename=filename,
        filepath=filepath,
        storage="local",
        filesize=filesize,
        checksum=checksum,
        class_name=class_name,
        subject=subject,
        chapter=chapter,
        status=PdfStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    session.add(pdf)
    await session.commit()
    await session.refresh(pdf)
    return pdf


async def process_pdf_background(
    pdf_id: int,
    local_path: str,
    filename: str,
    class_name: Optional[int] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    **kwargs,
):
    """
    Background worker: Load PDF -> Split -> Embed -> Store using LangChain.
    Uses naive UTC datetimes for database compatibility.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Update to PROCESSING
            await session.execute(
                update(PdfFile)
                .where(PdfFile.id == pdf_id)
                .values(status=PdfStatus.PROCESSING, updated_at=datetime.utcnow())
            )
            await session.commit()

            logger.info("Processing PDF with LangChain", extra={"pdf_id": pdf_id, "file": filename})

            # Step 1: Load and split PDF using LangChain
            docs = await load_and_split_pdf(
                file_path=local_path,
                source_file=filename,
                class_name=class_name,
                subject=subject,
                chapter=chapter,
            )

            if not docs:
                await session.execute(
                    update(PdfFile)
                    .where(PdfFile.id == pdf_id)
                    .values(
                        status=PdfStatus.FAILED,
                        last_error="No documents produced from PDF",
                        updated_at=datetime.utcnow()
                    )
                )
                await session.commit()
                return

            # Step 2: Embed and store in PGVector using LangChain
            result = await store_embeddings(docs)
            inserted = result["inserted"]

            logger.info(
                "PDF processed successfully",
                extra={
                    "pdf_id": pdf_id,
                    "inserted": inserted,
                    "file": filename,
                }
            )

            # Step 3: Update to PROCESSED
            await session.execute(
                update(PdfFile)
                .where(PdfFile.id == pdf_id)
                .values(
                    status=PdfStatus.PROCESSED,
                    chunks_count=inserted,
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()

            # Move file to processed folder
            try:
                dest = Path(PROCESSED) / filename
                shutil.move(local_path, dest)
            except Exception as e:
                logger.warning(f"Could not move file to processed: {e}")

        except Exception as exc:
            logger.error(
                "Error processing PDF",
                extra={"pdf_id": pdf_id, "error": str(exc)},
                exc_info=True,
            )

            await session.execute(
                update(PdfFile)
                .where(PdfFile.id == pdf_id)
                .values(
                    status=PdfStatus.FAILED,
                    last_error=str(exc),
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()

