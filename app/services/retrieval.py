# app/services/retrieval.py
from typing import List, Optional
from sqlalchemy import select, func, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_huggingface import HuggingFaceEmbeddings

from app.models.content import ContentChunk
from app.settings import settings
from app.logger import get_logger

logger = get_logger(__name__)


class ChunkResult:
    """Result from chunk retrieval."""
    def __init__(self, chunk: ContentChunk, similarity: float):
        self.chunk = chunk
        self.similarity = similarity


async def retrieve_chunks(
    session: AsyncSession,
    question: str,
    class_name: Optional[int] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    top_k: int = 8,
    similarity_threshold: float = 0.5,
) -> List[ChunkResult]:
    """
    Retrieve relevant chunks from ContentChunk table using pgvector similarity.
    Uses same mechanism as ingest - pgvector native similarity operators.

    Args:
        session: Database session
        question: User question to embed
        class_name: Filter by class
        subject: Filter by subject
        chapter: Filter by chapter
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score (0-1)

    Returns:
        List of ChunkResult with similarity scores
    """
    try:
        # Embed the question using same model as chunks
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        question_vector = embeddings.embed_query(question)

        # Build base query with pgvector similarity operator <=>
        # This uses cosine distance under the hood
        query = select(
            ContentChunk,
            (1 - (ContentChunk.embedding.cosine_distance(question_vector))).label("similarity")
        )

        # Add filters
        if class_name is not None:
            query = query.where(ContentChunk.class_name == class_name)
        if subject is not None:
            query = query.where(ContentChunk.subject == subject)
        if chapter is not None:
            query = query.where(ContentChunk.chapter == chapter)

        # Filter by similarity threshold and order by similarity descending
        query = query.where(
            (1 - (ContentChunk.embedding.cosine_distance(question_vector))) >= similarity_threshold
        ).order_by(
            desc((1 - (ContentChunk.embedding.cosine_distance(question_vector))))
        ).limit(top_k)

        # Execute query
        result = await session.execute(query)
        rows = result.all()

        if not rows:
            logger.info(
                "No chunks retrieved",
                extra={
                    "question": question[:50],
                    "class": class_name,
                    "subject": subject,
                    "chapter": chapter,
                }
            )
            return []

        # Convert rows to ChunkResult
        results = []
        for row in rows:
            chunk, similarity = row
            results.append(ChunkResult(chunk, float(similarity)))

        logger.info(
            "Retrieved chunks using pgvector",
            extra={
                "count": len(results),
                "question": question[:50],
                "avg_similarity": sum(r.similarity for r in results) / len(results) if results else 0,
            }
        )

        return results

    except Exception as e:
        logger.error("Error retrieving chunks", extra={"error": str(e)}, exc_info=True)
        return []


async def get_retrieval_stats(
    session: AsyncSession,
    class_name: Optional[int] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
) -> dict:
    """Get statistics about available chunks for filtering."""
    try:
        query = select(func.count(ContentChunk.id))

        if class_name is not None:
            query = query.where(ContentChunk.class_name == class_name)
        if subject is not None:
            query = query.where(ContentChunk.subject == subject)
        if chapter is not None:
            query = query.where(ContentChunk.chapter == chapter)

        result = await session.execute(query)
        count = result.first()

        return {"total_chunks_available": count or 0}
    except Exception as e:
        logger.error("Error getting stats", extra={"error": str(e)})
        return {"total_chunks_available": 0}

