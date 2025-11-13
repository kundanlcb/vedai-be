# app/crud/content.py
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.content import ContentChunk

async def create_chunk(session: AsyncSession, chunk_data: Dict[str, Any]) -> ContentChunk:
    chunk = ContentChunk(
        source_file=chunk_data.get("source_file"),
        class_name=chunk_data.get("class_name"),
        subject=chunk_data.get("subject"),
        chapter=chunk_data.get("chapter"),
        page=chunk_data.get("page"),
        text=chunk_data.get("text"),
        is_example=chunk_data.get("is_example", False),
        tokens=chunk_data.get("tokens"),
        created_at=datetime.utcnow(),
    )
    session.add(chunk)
    await session.commit()
    await session.refresh(chunk)
    return chunk

async def bulk_create_chunks(session: AsyncSession, chunks: List[Dict[str, Any]]) -> List[ContentChunk]:
    objs = [ContentChunk(
        source_file=c.get("source_file"),
        class_name=c.get("class_name"),
        subject=c.get("subject"),
        chapter=c.get("chapter"),
        page=c.get("page"),
        text=c.get("text"),
        is_example=c.get("is_example", False),
        tokens=c.get("tokens"),
        created_at=datetime.utcnow()
    ) for c in chunks]
    session.add_all(objs)
    await session.commit()
    for o in objs:
        await session.refresh(o)
    return objs

async def search_chunks_by_keyword(session: AsyncSession, keyword: str, limit: int = 10) -> List[ContentChunk]:
    pattern = f"%{keyword}%"
    q = select(ContentChunk).where(ContentChunk.text.ilike(pattern)).limit(limit)
    res = await session.exec(q)
    return res.all()