# app/routes/tests.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas.mock_test import (
    MockTestCreate,
    MockTestUpdate,
    MockTestRead,
    AttemptStart,
    AttemptRead,
    AttemptSubmit,
    AttemptDraftSave,
    AttemptStats,
)
from app.crud.mock_test import (
    get_test,
    list_tests,
    create_test,
    update_test,
    get_attempt,
    start_attempt,
    save_draft_answers,
    submit_attempt,
    get_student_attempts,
    get_student_stats,
)
from app.models import User
from app.utils.auth import get_current_user
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tests", tags=["Mock Tests"])


@router.get("/", response_model=List[MockTestRead])
async def list_mock_tests(
    subject: Optional[str] = Query(None),
    class_name: Optional[int] = Query(None, alias="class"),
    is_published: bool = Query(True),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    List available mock tests with optional filters.
    
    - **subject**: Filter by subject
    - **class**: Filter by class/grade
    - **is_published**: Show only published tests (default: true)
    - **limit**: Number of results (max 100)
    - **offset**: Pagination offset
    """
    tests = await list_tests(
        session,
        subject=subject,
        class_name=class_name,
        is_published=is_published,
        limit=limit,
        offset=offset,
    )
    return tests


@router.get("/{test_id}", response_model=MockTestRead)
async def get_mock_test(
    test_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific mock test"""
    test = await get_test(session, test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    if not test.is_published and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test is not published"
        )
    
    return test


@router.post("/", response_model=MockTestRead, status_code=status.HTTP_201_CREATED)
async def create_mock_test(
    test_data: MockTestCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new mock test.
    Admin/teacher only endpoint.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create tests"
        )
    
    test = await create_test(session, test_data.model_dump())
    logger.info(f"Created mock test: {test.id} - {test.title}")
    return test


@router.put("/{test_id}", response_model=MockTestRead)
async def update_mock_test(
    test_id: int,
    update_data: MockTestUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Update mock test (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update tests"
        )
    
    updated = await update_test(session, test_id, update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    logger.info(f"Updated mock test: {test_id}")
    return updated


@router.post("/{test_id}/start", response_model=AttemptRead, status_code=status.HTTP_201_CREATED)
async def start_mock_test(
    test_id: int,
    attempt_data: AttemptStart,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Start a new test attempt.
    Creates an attempt record and starts the timer.
    """
    # Verify test exists and is published
    test = await get_test(session, test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    if not test.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test is not published"
        )
    
    attempt = await start_attempt(session, test_id, attempt_data.student_id)
    logger.info(f"Started test attempt: {attempt.id} for test {test_id}")
    return attempt


@router.get("/attempts/{attempt_id}", response_model=AttemptRead)
async def get_test_attempt(
    attempt_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get details of a test attempt"""
    attempt = await get_attempt(session, attempt_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    return attempt


@router.patch("/attempts/{attempt_id}/draft", response_model=AttemptRead)
async def save_draft(
    attempt_id: int,
    draft_data: AttemptDraftSave,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Auto-save draft answers during test.
    Allows resuming the test if the app crashes.
    """
    attempt = await save_draft_answers(session, attempt_id, draft_data.answers)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    return attempt


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptRead)
async def submit_mock_test(
    attempt_id: int,
    submit_data: AttemptSubmit,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Submit test attempt with final answers.
    Calculates score and marks attempt as completed.
    """
    attempt = await submit_attempt(
        session,
        attempt_id,
        submit_data.answers,
        auto_submit=False,
    )
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )
    
    logger.info(f"Submitted test attempt: {attempt_id}, score: {attempt.percentage}%")
    return attempt


@router.get("/student/{student_id}/attempts", response_model=List[AttemptRead])
async def get_attempt_history(
    student_id: int,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get test attempt history for a student.
    Returns list of all attempts with results.
    """
    attempts = await get_student_attempts(session, student_id, limit, offset)
    return attempts


@router.get("/student/{student_id}/stats", response_model=AttemptStats)
async def get_student_statistics(
    student_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get performance statistics for a student.
    Includes overall and subject-wise metrics.
    """
    stats = await get_student_stats(session, student_id)
    return stats
