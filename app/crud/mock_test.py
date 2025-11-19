# app/crud/mock_test.py
from datetime import datetime, UTC
from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import MockTest, MockTestAttempt, AttemptStatus, Question
from app.crud.question import get_question


async def get_test(session: AsyncSession, test_id: int) -> Optional[MockTest]:
    """Get mock test by ID"""
    result = await session.execute(select(MockTest).where(MockTest.id == test_id))
    return result.scalar_one_or_none()


async def list_tests(
    session: AsyncSession,
    subject: Optional[str] = None,
    class_name: Optional[int] = None,
    is_published: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> List[MockTest]:
    """List mock tests with filters"""
    query = select(MockTest).where(MockTest.is_published == is_published)
    
    if subject:
        query = query.where(MockTest.subject == subject)
    if class_name:
        query = query.where(MockTest.class_name == class_name)
    
    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_test(session: AsyncSession, test_data: dict) -> MockTest:
    """Create a new mock test"""
    test = MockTest(**test_data)
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


async def update_test(session: AsyncSession, test_id: int, update_data: dict) -> Optional[MockTest]:
    """Update mock test"""
    test = await get_test(session, test_id)
    if not test:
        return None
    
    for key, value in update_data.items():
        if value is not None:
            setattr(test, key, value)
    
    test.updated_at = datetime.now(UTC)
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


async def get_attempt(session: AsyncSession, attempt_id: int) -> Optional[MockTestAttempt]:
    """Get test attempt by ID"""
    result = await session.execute(select(MockTestAttempt).where(MockTestAttempt.id == attempt_id))
    return result.scalar_one_or_none()


async def start_attempt(session: AsyncSession, test_id: int, student_id: int) -> MockTestAttempt:
    """Start a new test attempt"""
    attempt = MockTestAttempt(
        test_id=test_id,
        student_id=student_id,
        status=AttemptStatus.IN_PROGRESS,
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def save_draft_answers(
    session: AsyncSession,
    attempt_id: int,
    answers: dict,
) -> Optional[MockTestAttempt]:
    """Save draft answers (auto-save)"""
    attempt = await get_attempt(session, attempt_id)
    if not attempt:
        return None
    
    # Merge new answers with existing
    attempt.answers.update(answers)
    attempt.updated_at = datetime.now(UTC)
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def submit_attempt(
    session: AsyncSession,
    attempt_id: int,
    answers: dict,
    auto_submit: bool = False,
) -> Optional[MockTestAttempt]:
    """Submit test attempt and calculate score"""
    attempt = await get_attempt(session, attempt_id)
    if not attempt:
        return None
    
    if attempt.status != AttemptStatus.IN_PROGRESS:
        return attempt  # Already submitted
    
    # Get the test
    test = await get_test(session, attempt.test_id)
    if not test:
        return None
    
    # Update answers
    attempt.answers = answers
    attempt.end_time = datetime.now(UTC)
    attempt.status = AttemptStatus.AUTO_SUBMITTED if auto_submit else AttemptStatus.SUBMITTED
    
    # Calculate score
    questions_attempted = len(answers)
    questions_correct = 0
    obtained_marks = 0
    
    for question_id_str, student_answer in answers.items():
        try:
            question_id = int(question_id_str)
            question = await get_question(session, question_id)
            
            if not question:
                continue
            
            # For MCQ, check if selected option is correct
            if question.question_type.value == "mcq":
                for option in question.options:
                    if option.id == student_answer and option.is_correct:
                        questions_correct += 1
                        obtained_marks += question.marks or 1
                        break
            # For other types, would need manual grading (future enhancement)
            
        except (ValueError, TypeError):
            continue
    
    attempt.questions_attempted = questions_attempted
    attempt.questions_correct = questions_correct
    attempt.obtained_marks = obtained_marks
    attempt.percentage = (obtained_marks / test.total_marks * 100) if test.total_marks > 0 else 0.0
    
    attempt.updated_at = datetime.now(UTC)
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def get_student_attempts(
    session: AsyncSession,
    student_id: int,
    limit: int = 50,
    offset: int = 0,
) -> List[MockTestAttempt]:
    """Get attempt history for a student"""
    query = select(MockTestAttempt).where(
        MockTestAttempt.student_id == student_id
    ).order_by(MockTestAttempt.created_at.desc()).offset(offset).limit(limit)
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_student_stats(session: AsyncSession, student_id: int) -> dict:
    """Get test statistics for a student"""
    attempts = await get_student_attempts(session, student_id, limit=1000)
    
    if not attempts:
        return {
            "student_id": student_id,
            "total_attempts": 0,
            "avg_percentage": 0.0,
            "total_time_minutes": 0,
            "subject_wise_stats": {},
        }
    
    # Filter only submitted attempts
    submitted = [a for a in attempts if a.status in [AttemptStatus.SUBMITTED, AttemptStatus.AUTO_SUBMITTED]]
    
    if not submitted:
        return {
            "student_id": student_id,
            "total_attempts": len(attempts),
            "avg_percentage": 0.0,
            "total_time_minutes": 0,
            "subject_wise_stats": {},
        }
    
    # Calculate overall stats
    total_percentage = sum(a.percentage for a in submitted)
    avg_percentage = total_percentage / len(submitted)
    
    # Calculate time spent
    total_time = 0
    for a in submitted:
        if a.end_time and a.start_time:
            duration = (a.end_time - a.start_time).total_seconds() / 60
            total_time += duration
    
    # Subject-wise stats (would need to fetch tests for each attempt)
    subject_stats = {}
    
    return {
        "student_id": student_id,
        "total_attempts": len(submitted),
        "avg_percentage": round(avg_percentage, 2),
        "total_time_minutes": int(total_time),
        "subject_wise_stats": subject_stats,
    }
