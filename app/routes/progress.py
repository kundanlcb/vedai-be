# app/routes/progress.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas.progress import ProgressCreate, ProgressUpdate, ProgressRead, ProgressOverview
from app.crud.progress import (
    get_progress,
    get_student_progress,
    create_progress,
    update_progress,
    get_progress_overview,
)
from app.models import User
from app.utils.auth import get_current_user
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.post("/", response_model=ProgressRead, status_code=status.HTTP_201_CREATED)
async def create_progress_entry(
    progress_data: ProgressCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new progress entry.
    Tracks student's progress on a specific chapter.
    """
    progress = await create_progress(session, progress_data.model_dump())
    logger.info(f"Created progress entry: {progress.id} for student {progress.student_id}")
    return progress


@router.get("/{progress_id}", response_model=ProgressRead)
async def get_progress_entry(
    progress_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get specific progress entry by ID"""
    progress = await get_progress(session, progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress entry not found"
        )
    return progress


@router.put("/{progress_id}", response_model=ProgressRead)
async def update_progress_entry(
    progress_id: int,
    update_data: ProgressUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Update progress entry"""
    updated = await update_progress(
        session,
        progress_id,
        update_data.model_dump(exclude_unset=True)
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress entry not found"
        )
    
    logger.info(f"Updated progress entry: {progress_id}")
    return updated


@router.get("/student/{student_id}", response_model=List[ProgressRead])
async def get_student_progress_list(
    student_id: int,
    subject: Optional[str] = Query(None),
    chapter: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get all progress entries for a student.
    Optional filters by subject and/or chapter.
    """
    progress_list = await get_student_progress(
        session,
        student_id,
        subject=subject,
        chapter=chapter,
    )
    return progress_list


@router.get("/student/{student_id}/overview", response_model=ProgressOverview)
async def get_student_progress_overview(
    student_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated progress overview for a student.
    Returns statistics grouped by subject.
    """
    overview = await get_progress_overview(session, student_id)
    return overview
