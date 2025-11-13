# app/vector/store.py
"""
Utilities to persist embeddings + text into Postgres (PGVector) using SQLModel/SQLAlchemy.
Provides `save_embeddings(session, chunks_batch, vectors_batch)` where
`chunks_batch` is a list of chunk dicts (matching chunk_pdf output) and
`vectors_batch` is a list of vectors aligned with chunks_batch.
"""
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.content import ContentChunk


async def check_embedding_exists(
    session: AsyncSession,
    text: str,
    class_name: int | None = None,
    subject: str | None = None,
    chapter: str | None = None,
) -> bool:
    """Check if this exact chunk already exists for the same class/subject/chapter.

    Uses composite key: (text, class_name, subject, chapter)
    """
    query = select(ContentChunk).where(
        ContentChunk.text == text,
        ContentChunk.class_name == class_name,
        ContentChunk.subject == subject,
        ContentChunk.chapter == chapter,
    )
    result = await session.execute(query)
    return result.scalars().first() is not None


async def save_embeddings(
    session: AsyncSession,
    chunks_batch: List[Dict[str, Any]],
    vectors_batch: List[List[float]]
) -> Dict[str, int]:
    """Persist a batch of chunks with their embeddings into ContentChunk table.

    Skips duplicates based on composite key (text, class_name, subject, chapter).

    Returns dict with counts: {"inserted": count, "skipped": count}
    """
    if len(chunks_batch) != len(vectors_batch):
        raise ValueError("chunks_batch and vectors_batch must be same length")

    objs = []
    skipped = 0

    for c, vec in zip(chunks_batch, vectors_batch):
        # Check for duplicates
        exists = await check_embedding_exists(
            session,
            text=c.get("text"),
            class_name=c.get("class_name"),
            subject=c.get("subject"),
            chapter=c.get("chapter"),
        )

        if exists:
            skipped += 1
            continue

        obj = ContentChunk(
            source_file=c.get("source_file"),
            class_name=c.get("class_name"),
            subject=c.get("subject"),
            chapter=c.get("chapter"),
            page=c.get("page"),
            text=c.get("text"),
            embedding=vec,
            is_example=c.get("is_example", False),
            tokens=c.get("tokens"),
            created_at=datetime.utcnow(),
        )
        objs.append(obj)

    if objs:
        session.add_all(objs)
        await session.commit()
        for o in objs:
            await session.refresh(o)

    return {"inserted": len(objs), "skipped": skipped}
