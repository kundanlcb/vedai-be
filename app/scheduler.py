# app/scheduler.py
import asyncio
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from sqlalchemy import update, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import AsyncSessionLocal
from app.models.ingest import PdfFile, PdfStatus
from app.utils.chunker import chunk_pdf  # your chunker
# from app.embeddings import embed_batch  # implement provider-specific embedding

PDF_DIR = Path("pdfs")
INCOMING = PDF_DIR / "incoming"
PROCESSING = PDF_DIR / "processing"
PROCESSED = PDF_DIR / "processed"
FAILED = PDF_DIR / "failed"

# Ensure folders exist
for d in (INCOMING, PROCESSING, PROCESSED, FAILED):
    d.mkdir(parents=True, exist_ok=True)


async def compute_sha256(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(chunk_size), b""):
            h.update(b)
    return h.hexdigest()


async def claim_next_pdf(session: AsyncSession) -> Optional[PdfFile]:
    """
    Atomically find one pending row and mark it CLAIMED.
    We do this with an UPDATE ... WHERE id = (SELECT id ... LIMIT 1 FOR UPDATE SKIP LOCKED)
    Simpler approach: SELECT id for update skip locked - then UPDATE.
    We'll use a two-step with optimistic update via row id to avoid DB-specific quirks.
    """
    # 1) find candidate
    stmt = select(PdfFile).where(PdfFile.status == PdfStatus.PENDING).order_by(PdfFile.created_at).limit(1)
    result = await session.exec(stmt)
    candidate = result.first()
    if not candidate:
        return None

    # 2) try to update status from PENDING -> CLAIMED (check rowcount to avoid race)
    upd = update(PdfFile).where(PdfFile.id == candidate.id, PdfFile.status == PdfStatus.PENDING).values(
        status=PdfStatus.CLAIMED, updated_at=datetime.utcnow()
    ).execution_options(synchronize_session="fetch")
    res = await session.execute(upd)
    if res.rowcount == 0:
        # someone else claimed it
        await session.commit()
        return None
    await session.commit()

    # reload fresh row
    stmt2 = select(PdfFile).where(PdfFile.id == candidate.id)
    res2 = await session.exec(stmt2)
    return res2.first()


async def process_pdf_row(row: PdfFile):
    """
    Do the filesystem moves and run ingestion.
    """
    session_maker = AsyncSessionLocal
    async with session_maker() as session:
        try:
            # move file incoming -> processing
            src = Path(row.filepath)
            dest = PROCESSING / src.name
            shutil.move(str(src), str(dest))

            # update DB to processing
            await session.execute(
                update(PdfFile)
                .where(PdfFile.id == row.id)
                .values(status=PdfStatus.PROCESSING, filepath=str(dest), updated_at=datetime.utcnow())
            )
            await session.commit()

            # Run ingestion pipeline (chunk -> embed -> insert)
            chunks = list(chunk_pdf(str(dest), source_file=dest.name))
            chunks_count = len(chunks)

            # EXAMPLE: embed in batches (implement embed_batch)
            # vectors = []
            # BATCH = 128
            # for i in range(0, len(chunks), BATCH):
            #     texts = [c["text"] for c in chunks[i : i + BATCH]]
            #     vecs = await embed_batch(texts)
            #     vectors.extend(vecs)
            # TODO: insert into vector DB along with chunk metadata.

            # For now just update chunks_count and pages (if you parse that)
            await session.execute(
                update(PdfFile)
                .where(PdfFile.id == row.id)
                .values(chunks_count=chunks_count, status=PdfStatus.PROCESSED, updated_at=datetime.utcnow())
            )
            await session.commit()

            # move to processed folder
            final = PROCESSED / dest.name
            shutil.move(str(dest), str(final))

        except Exception as exc:
            # mark failed
            await session.execute(
                update(PdfFile)
                .where(PdfFile.id == row.id)
                .values(status=PdfStatus.FAILED, last_error=str(exc), updated_at=datetime.utcnow())
            )
            await session.commit()
            # move to failed folder (if exists)
            try:
                bad = FAILED / Path(row.filepath).name
                shutil.move(str(dest), str(bad))
            except Exception:
                pass
            # log & re-raise optionally
            print("Processing failed:", exc)


async def worker_iteration():
    """
    Attempt to claim and process as many items as available, one-by-one.
    Keep this fast to allow periodic scheduling.
    """
    async with AsyncSessionLocal() as session:
        row = await claim_next_pdf(session)
    while row:
        # process each row in background (sequential here; you can parallelize carefully)
        await process_pdf_row(row)
        async with AsyncSessionLocal() as session:
            row = await claim_next_pdf(session)


def start_scheduler(interval_seconds: int = 10):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(worker_iteration, IntervalTrigger(seconds=interval_seconds))
    scheduler.start()
    return scheduler