# app/crud/student.py
from datetime import datetime, UTC
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Student


async def get_student(session: AsyncSession, student_id: int) -> Optional[Student]:
    """Get student by ID"""
    result = await session.exec(select(Student).where(Student.id == student_id))
    return result.first()


async def get_student_by_user_id(session: AsyncSession, user_id: int) -> Optional[Student]:
    """Get student by user ID"""
    result = await session.exec(select(Student).where(Student.user_id == user_id))
    return result.first()


async def create_student(session: AsyncSession, student_data: dict) -> Student:
    """Create a new student profile"""
    student = Student(**student_data)
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


async def update_student(session: AsyncSession, student_id: int, update_data: dict) -> Optional[Student]:
    """Update student profile"""
    student = await get_student(session, student_id)
    if not student:
        return None
    
    # Update only provided fields
    for key, value in update_data.items():
        if value is not None:
            setattr(student, key, value)
    
    student.updated_at = datetime.now(UTC)
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


async def delete_student(session: AsyncSession, student_id: int) -> bool:
    """Delete student profile"""
    student = await get_student(session, student_id)
    if not student:
        return False
    
    await session.delete(student)
    await session.commit()
    return True
