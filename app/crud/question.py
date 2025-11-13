# app/crud/question.py
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.question import Question, QuestionOption, QuestionType
from app.schemas import OptionCreate


async def create_question_with_options(
    session: AsyncSession,
    *,
    text: str,
    question_type: QuestionType,
    marks: Optional[int] = 1,
    year: Optional[int] = None,
    source_board: Optional[str] = None,
    chapter: Optional[str] = None,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    generated: bool = False,
    options: Optional[List[OptionCreate]] = None,
) -> Question:
    """
    Create a Question and associated QuestionOption rows (if provided).
    Returns the created Question with options relationship loaded.
    """
    q = Question(
        text=text,
        question_type=question_type,
        marks=marks,
        year=year,
        source_board=source_board,
        chapter=chapter,
        subject=subject,
        difficulty=difficulty,
        generated=generated,
        created_at=datetime.utcnow(),
    )
    session.add(q)
    await session.flush()  # q.id is available now

    created_opts: List[QuestionOption] = []
    if options:
        for opt in options:
            o = QuestionOption(question_id=q.id, text=opt.text, is_correct=opt.is_correct)
            session.add(o)
            created_opts.append(o)

    await session.commit()

    # Re-query question with options using selectinload to ensure relationship populated
    stmt = select(Question).where(Question.id == q.id).options(selectinload(Question.options))
    result = await session.exec(stmt)
    created_question: Optional[Question] = result.scalar_one_or_none()
    if created_question is None:
        # This should not happen; raise or return q (but raising better surfaces issues)
        raise RuntimeError("Failed to load newly created Question from DB")

    return created_question


async def get_question(session: AsyncSession, question_id: int) -> Optional[Question]:
    """
    Fetch a question by id and eagerly load options (if any).
    Returns None if not found.
    """
    stmt = select(Question).where(Question.id == question_id).options(selectinload(Question.options))
    res = await session.exec(stmt)
    return res.scalar_one_or_none()


async def list_questions(
    session: AsyncSession,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Question]:
    """
    List recent questions with optional filtering by subject and chapter.
    Options relationship is selectinloaded for each question.
    """
    stmt = select(Question).order_by(Question.created_at.desc()).offset(offset).limit(limit)
    if subject:
        stmt = stmt.where(Question.subject == subject)
    if chapter:
        stmt = stmt.where(Question.chapter == chapter)

    stmt = stmt.options(selectinload(Question.options))
    res = await session.exec(stmt)
    return res.scalars().all()