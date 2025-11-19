# app/crud/progress.py
from datetime import datetime, UTC
from typing import List, Optional

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import ProgressEntry


async def get_progress(session: AsyncSession, progress_id: int) -> Optional[ProgressEntry]:
    """Get progress entry by ID"""
    result = await session.execute(select(ProgressEntry).where(ProgressEntry.id == progress_id))
    return result.scalar_one_or_none()


async def get_student_progress(
    session: AsyncSession,
    student_id: int,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
) -> List[ProgressEntry]:
    """Get progress entries for a student"""
    query = select(ProgressEntry).where(ProgressEntry.student_id == student_id)
    
    if subject:
        query = query.where(ProgressEntry.subject == subject)
    if chapter:
        query = query.where(ProgressEntry.chapter == chapter)
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_or_create_progress(
    session: AsyncSession,
    student_id: int,
    subject: str,
    chapter: str,
    class_name: int,
) -> ProgressEntry:
    """Get existing progress entry or create new one"""
    query = select(ProgressEntry).where(
        ProgressEntry.student_id == student_id,
        ProgressEntry.subject == subject,
        ProgressEntry.chapter == chapter,
    )
    result = await session.execute(query)
    progress = result.scalar_one_or_none()
    
    if progress:
        return progress
    
    # Create new progress entry
    progress = ProgressEntry(
        student_id=student_id,
        subject=subject,
        chapter=chapter,
        class_name=class_name,
    )
    session.add(progress)
    await session.commit()
    await session.refresh(progress)
    return progress


async def create_progress(session: AsyncSession, progress_data: dict) -> ProgressEntry:
    """Create a new progress entry"""
    progress = ProgressEntry(**progress_data)
    session.add(progress)
    await session.commit()
    await session.refresh(progress)
    return progress


async def update_progress(
    session: AsyncSession,
    progress_id: int,
    update_data: dict,
) -> Optional[ProgressEntry]:
    """Update progress entry"""
    progress = await get_progress(session, progress_id)
    if not progress:
        return None
    
    for key, value in update_data.items():
        if value is not None:
            setattr(progress, key, value)
    
    # Check if completed
    if progress.completion_percentage >= 100:
        progress.is_completed = True
    
    progress.updated_at = datetime.now(UTC)
    session.add(progress)
    await session.commit()
    await session.refresh(progress)
    return progress


async def get_progress_overview(session: AsyncSession, student_id: int) -> dict:
    """Get aggregated progress overview for a student"""
    # Get all progress entries for the student
    entries = await get_student_progress(session, student_id)
    
    if not entries:
        return {
            "student_id": student_id,
            "subjects": [],
            "total_time_minutes": 0,
            "overall_completion": 0.0,
        }
    
    # Group by subject
    subject_data = {}
    total_time = 0
    total_completion = 0
    
    for entry in entries:
        if entry.subject not in subject_data:
            subject_data[entry.subject] = {
                "subject": entry.subject,
                "chapters": [],
                "total_time": 0,
            }
        
        subject_data[entry.subject]["chapters"].append(entry)
        subject_data[entry.subject]["total_time"] += entry.time_spent_minutes
        total_time += entry.time_spent_minutes
        total_completion += entry.completion_percentage
    
    # Calculate aggregates
    subjects = []
    for subject, data in subject_data.items():
        chapters = data["chapters"]
        completed = sum(1 for c in chapters if c.is_completed)
        avg_completion = sum(c.completion_percentage for c in chapters) / len(chapters)
        
        subjects.append({
            "subject": subject,
            "total_chapters": len(chapters),
            "completed_chapters": completed,
            "avg_completion": round(avg_completion, 2),
            "total_time_minutes": data["total_time"],
        })
    
    overall_completion = total_completion / len(entries) if entries else 0.0
    
    return {
        "student_id": student_id,
        "subjects": subjects,
        "total_time_minutes": total_time,
        "overall_completion": round(overall_completion, 2),
    }
