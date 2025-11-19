#!/usr/bin/env python
"""
Test script for VedAI production-ready APIs
Tests authentication, student profiles, progress tracking, and mock tests.
"""
import asyncio
import sys
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# Import from app
from app.db import AsyncSessionLocal, init_db
from app.crud.user import create_user, authenticate_user
from app.crud.student import create_student, get_student_by_user_id, update_student
from app.crud.progress import create_progress, get_student_progress, get_progress_overview
from app.crud.question import create_question_with_options
from app.crud.mock_test import (
    create_test,
    list_tests,
    start_attempt,
    save_draft_answers,
    submit_attempt,
    get_student_stats,
)
from app.models import User, Student, Question, QuestionType
from app.schemas.question import OptionCreate
from app.utils.security import create_access_token, decode_access_token


async def test_authentication():
    """Test user authentication and JWT tokens"""
    print("\n" + "=" * 60)
    print("Testing Authentication System")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Create a test user
        print("\n1. Creating test user...")
        user = await create_user(
            session=session,
            email="test@vedai.com",
            password="testpass123",
            is_superuser=False,
        )
        print(f"   ✓ User created: ID={user.id}, Email={user.email}")
        
        # Test authentication
        print("\n2. Testing authentication...")
        auth_user = await authenticate_user(session, "test@vedai.com", "testpass123")
        assert auth_user is not None, "Authentication failed"
        print(f"   ✓ Authentication successful")
        
        # Test JWT token creation and decoding
        print("\n3. Testing JWT tokens...")
        token = create_access_token(data={"sub": str(user.id)})
        print(f"   ✓ JWT token created: {token[:50]}...")
        
        decoded = decode_access_token(token)
        assert decoded is not None, "Token decoding failed"
        assert int(decoded["sub"]) == user.id, "Token user ID mismatch"
        print(f"   ✓ Token decoded successfully: user_id={decoded['sub']}")
        
        return user


async def test_student_profile(user: User):
    """Test student profile CRUD operations"""
    print("\n" + "=" * 60)
    print("Testing Student Profile Management")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Create student profile
        print("\n1. Creating student profile...")
        student = await create_student(session, {
            "user_id": user.id,
            "name": "Test Student",
            "class_name": 10,
            "medium": "English",
            "subjects": "Math,Science,English",
            "board": "CBSE",
        })
        print(f"   ✓ Student created: ID={student.id}, Name={student.name}, Class={student.class_name}")
        
        # Get student by user ID
        print("\n2. Retrieving student profile...")
        retrieved = await get_student_by_user_id(session, user.id)
        assert retrieved is not None, "Student not found"
        assert retrieved.id == student.id, "Student ID mismatch"
        print(f"   ✓ Student retrieved successfully")
        
        # Update student profile
        print("\n3. Updating student profile...")
        updated = await update_student(session, student.id, {
            "name": "Updated Student Name",
            "class_name": 11,
        })
        assert updated.name == "Updated Student Name", "Name not updated"
        assert updated.class_name == 11, "Class not updated"
        print(f"   ✓ Student updated: Name={updated.name}, Class={updated.class_name}")
        
        return student


async def test_progress_tracking(student: Student):
    """Test progress tracking functionality"""
    print("\n" + "=" * 60)
    print("Testing Progress Tracking")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Create progress entries for multiple chapters
        print("\n1. Creating progress entries...")
        subjects_chapters = [
            ("Math", "Algebra", 45),
            ("Math", "Geometry", 80),
            ("Science", "Physics", 60),
            ("Science", "Chemistry", 30),
        ]
        
        for subject, chapter, completion in subjects_chapters:
            progress = await create_progress(session, {
                "student_id": student.id,
                "subject": subject,
                "chapter": chapter,
                "class_name": student.class_name,
                "completion_percentage": completion,
                "time_spent_minutes": completion * 2,  # Simulate time spent
                "chunks_viewed": completion // 10,
            })
            print(f"   ✓ Progress created: {subject} - {chapter} ({completion}%)")
        
        # Get student progress
        print("\n2. Retrieving student progress...")
        all_progress = await get_student_progress(session, student.id)
        print(f"   ✓ Total progress entries: {len(all_progress)}")
        
        # Get progress for specific subject
        math_progress = await get_student_progress(session, student.id, subject="Math")
        print(f"   ✓ Math progress entries: {len(math_progress)}")
        
        # Get progress overview
        print("\n3. Getting progress overview...")
        overview = await get_progress_overview(session, student.id)
        print(f"   ✓ Total subjects: {len(overview['subjects'])}")
        print(f"   ✓ Total time spent: {overview['total_time_minutes']} minutes")
        print(f"   ✓ Overall completion: {overview['overall_completion']}%")
        
        for subject in overview['subjects']:
            print(f"     - {subject['subject']}: {subject['completed_chapters']}/{subject['total_chapters']} chapters, {subject['avg_completion']}% avg")


async def test_mock_tests(student: Student):
    """Test mock test system"""
    print("\n" + "=" * 60)
    print("Testing Mock Test System")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # First, create some test questions
        print("\n1. Creating test questions...")
        question_ids = []
        
        for i in range(5):
            question = await create_question_with_options(
                session=session,
                text=f"What is the value of {i} + {i}?",
                question_type=QuestionType.MCQ,
                marks=2,
                subject="Math",
                chapter="Algebra",
                difficulty="easy",
                generated=False,
                options=[
                    OptionCreate(text=f"{i + i}", is_correct=True),
                    OptionCreate(text=f"{i + i + 1}", is_correct=False),
                    OptionCreate(text=f"{i + i - 1}", is_correct=False),
                    OptionCreate(text=f"{i * 2 + 1}", is_correct=False),
                ],
            )
            question_ids.append(question.id)
            print(f"   ✓ Question {i+1} created (ID: {question.id})")
        
        # Create a mock test
        print("\n2. Creating mock test...")
        test = await create_test(session, {
            "title": "Math - Algebra Test",
            "description": "Test your algebra skills",
            "subject": "Math",
            "chapter": "Algebra",
            "class_name": student.class_name,
            "total_questions": len(question_ids),
            "total_marks": len(question_ids) * 2,
            "duration_minutes": 30,
            "passing_marks": 6,
            "question_ids": question_ids,
            "is_published": True,
        })
        print(f"   ✓ Test created: ID={test.id}, Title={test.title}")
        
        # List tests
        print("\n3. Listing available tests...")
        tests = await list_tests(session, subject="Math", class_name=student.class_name)
        print(f"   ✓ Found {len(tests)} test(s)")
        
        # Start an attempt
        print("\n4. Starting test attempt...")
        attempt = await start_attempt(session, test.id, student.id)
        print(f"   ✓ Attempt started: ID={attempt.id}, Status={attempt.status}")
        
        # Save draft answers
        print("\n5. Saving draft answers...")
        draft_answers = {
            str(question_ids[0]): question_ids[0] + 1,  # First answer (will check correctness later)
            str(question_ids[1]): question_ids[1] + 1,
        }
        draft_attempt = await save_draft_answers(session, attempt.id, draft_answers)
        print(f"   ✓ Draft saved: {len(draft_attempt.answers)} answer(s)")
        
        # Get the actual questions to find correct answers
        print("\n6. Preparing final answers...")
        final_answers = {}
        for qid in question_ids:
            result = await session.execute(select(Question).where(Question.id == qid))
            question = result.scalar_one_or_none()
            if question and question.options:
                # Find the correct option
                for option in question.options:
                    if option.is_correct:
                        final_answers[str(qid)] = option.id
                        break
        
        # Submit the test
        print("\n7. Submitting test...")
        submitted = await submit_attempt(session, attempt.id, final_answers)
        print(f"   ✓ Test submitted:")
        print(f"     - Questions attempted: {submitted.questions_attempted}")
        print(f"     - Questions correct: {submitted.questions_correct}")
        print(f"     - Marks obtained: {submitted.obtained_marks}/{test.total_marks}")
        print(f"     - Percentage: {submitted.percentage:.2f}%")
        print(f"     - Status: {submitted.status}")
        
        # Get student stats
        print("\n8. Getting student statistics...")
        stats = await get_student_stats(session, student.id)
        print(f"   ✓ Total attempts: {stats['total_attempts']}")
        print(f"   ✓ Average percentage: {stats['avg_percentage']:.2f}%")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("VedAI Production API Test Suite")
    print("=" * 60)
    
    try:
        # Initialize database
        print("\nInitializing database...")
        await init_db()
        print("✓ Database initialized")
        
        # Run tests
        user = await test_authentication()
        student = await test_student_profile(user)
        await test_progress_tracking(student)
        await test_mock_tests(student)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
