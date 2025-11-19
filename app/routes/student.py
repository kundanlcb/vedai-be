# app/routes/student.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas.student import StudentCreate, StudentUpdate, StudentRead
from app.crud.student import (
    get_student,
    get_student_by_user_id,
    create_student,
    update_student,
    delete_student,
)
from app.models import User
from app.utils.auth import get_current_user
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/register", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def register_student(
    student_data: StudentCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create a new student profile.
    Used during registration process.
    """
    # Check if student profile already exists for this user
    existing = await get_student_by_user_id(session, student_data.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile already exists for this user"
        )
    
    student = await create_student(session, student_data.model_dump())
    logger.info(f"Created student profile: {student.id}")
    return student


@router.get("/{student_id}", response_model=StudentRead)
async def get_student_profile(
    student_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get student profile by ID"""
    student = await get_student(session, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Optionally check if current user owns this profile
    # For now, allow any authenticated user to view
    
    return student


@router.get("/user/{user_id}", response_model=StudentRead)
async def get_student_by_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get student profile by user ID"""
    student = await get_student_by_user_id(session, user_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )
    
    return student


@router.put("/{student_id}", response_model=StudentRead)
async def update_student_profile(
    student_id: int,
    update_data: StudentUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Update student profile"""
    # Verify student belongs to current user
    student = await get_student(session, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if student.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    updated_student = await update_student(
        session,
        student_id,
        update_data.model_dump(exclude_unset=True)
    )
    
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update student"
        )
    
    logger.info(f"Updated student profile: {student_id}")
    return updated_student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_profile(
    student_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Delete student profile"""
    # Verify student belongs to current user or user is admin
    student = await get_student(session, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if student.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this profile"
        )
    
    success = await delete_student(session, student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete student"
        )
    
    logger.info(f"Deleted student profile: {student_id}")
    return None
