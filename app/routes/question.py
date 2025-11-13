# app/routes/question.py
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas.question import QuestionCreate, QuestionRead, OptionCreate, OptionRead
from app.crud import create_question_with_options, get_question, list_questions
from app.models.question import QuestionType

router = APIRouter(prefix="/questions", tags=["questions"]) 


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    payload: QuestionCreate, session: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Create a question. For MCQ questions, include `options` with at least one `is_correct=True`.
    """
    # Validate basic invariants
    if payload.question_type == QuestionType.MCQ:
        if not payload.options or len(payload.options) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MCQ must include at least two options.",
            )
        if not any(o.is_correct for o in payload.options):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MCQ must include at least one correct option (is_correct=True).",
            )

    # create question (crud handles inserting options if provided)
    created = await create_question_with_options(
        session=session,
        text=payload.text,
        question_type=payload.question_type,
        marks=payload.marks,
        year=payload.year,
        source_board=payload.source_board,
        chapter=payload.chapter,
        subject=payload.subject,
        difficulty=payload.difficulty,
        generated=payload.generated,
        options=payload.options,
    )
    # Fetch & return in read schema (crud already refreshes)
    q = await get_question(session, created.id)
    if not q:
        raise HTTPException(status_code=500, detail="Failed to create question")
    return q


@router.get("/{question_id}", response_model=QuestionRead)
async def read_question(question_id: int, session: AsyncSession = Depends(get_async_session)) -> Any:
    q = await get_question(session, question_id)
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return q


@router.get("/", response_model=List[QuestionRead])
async def list_questions_endpoint(
    subject: Optional[str] = Query(None),
    chapter: Optional[str] = Query(None),
    limit: int = Query(50, gt=0, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    results = await list_questions(session=session, subject=subject, chapter=chapter, limit=limit, offset=offset)
    return results