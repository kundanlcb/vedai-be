# app/schemas/mock_test.py
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class MockTestCreate(BaseModel):
    """Create a new mock test (admin only)"""
    title: str = Field(..., description="Test title", min_length=1, examples=["Class 10 Physics Mid-Term Test"])
    description: Optional[str] = Field(default=None, description="Test description", examples=["Covers chapters 1-5"])
    subject: str = Field(..., description="Subject name", examples=["Physics"])
    chapter: Optional[str] = Field(default=None, description="Chapter/topic", examples=["Light and Reflection"])
    class_name: int = Field(..., description="Class/Grade", ge=8, le=12, examples=[10])
    total_questions: int = Field(..., description="Total questions in test", gt=0, examples=[30])
    total_marks: int = Field(..., description="Total marks", gt=0, examples=[100])
    duration_minutes: int = Field(..., description="Test duration in minutes", gt=0, examples=[60])
    passing_marks: int = Field(..., description="Minimum marks to pass", gt=0, examples=[40])
    question_ids: List[int] = Field(..., description="List of question IDs", examples=[[1, 2, 3, 4, 5]])
    is_published: bool = Field(default=False, description="Published status", examples=[True])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Class 10 Physics Mid-Term Test",
                    "description": "Covers Light, Electricity, and Magnetism",
                    "subject": "Physics",
                    "chapter": "Light and Reflection",
                    "class_name": 10,
                    "total_questions": 30,
                    "total_marks": 100,
                    "duration_minutes": 60,
                    "passing_marks": 40,
                    "question_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "is_published": True
                }
            ]
        }
    }


class MockTestUpdate(BaseModel):
    """Update mock test details (admin only)"""
    title: Optional[str] = Field(default=None, description="Updated title", examples=["Updated Test Title"])
    description: Optional[str] = Field(default=None, description="Updated description", examples=["New description"])
    is_published: Optional[bool] = Field(default=None, description="Published status", examples=[True])


class MockTestRead(BaseModel):
    """Mock test details with metadata"""
    id: int = Field(..., description="Test ID", examples=[1])
    title: str = Field(..., description="Test title", examples=["Class 10 Physics Mid-Term Test"])
    description: Optional[str] = Field(default=None, description="Test description")
    subject: str = Field(..., description="Subject", examples=["Physics"])
    chapter: Optional[str] = Field(default=None, description="Chapter", examples=["Light and Reflection"])
    class_name: int = Field(..., description="Class/Grade", examples=[10])
    total_questions: int = Field(..., description="Total questions", examples=[30])
    total_marks: int = Field(..., description="Total marks", examples=[100])
    duration_minutes: int = Field(..., description="Duration in minutes", examples=[60])
    passing_marks: int = Field(..., description="Passing marks", examples=[40])
    question_ids: List[int] = Field(..., description="Question IDs", examples=[[1, 2, 3]])
    is_published: bool = Field(..., description="Published status", examples=[True])
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {"from_attributes": True}


class AttemptStart(BaseModel):
    """Start a new test attempt"""
    test_id: int = Field(..., description="Test ID to attempt", examples=[1])
    student_id: int = Field(..., description="Student ID", examples=[1])


class AttemptRead(BaseModel):
    """Test attempt details with results"""
    id: int = Field(..., description="Attempt ID", examples=[1])
    test_id: int = Field(..., description="Test ID", examples=[1])
    student_id: int = Field(..., description="Student ID", examples=[1])
    status: str = Field(..., description="Attempt status", examples=["in_progress", "submitted"])
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(default=None, description="End time")
    answers: Dict[str, int | str] = Field(..., description="Student answers", examples=[{"1": 2, "2": "Short answer text"}])
    questions_attempted: int = Field(..., description="Questions attempted", examples=[25])
    questions_correct: int = Field(..., description="Correct answers", examples=[20])
    obtained_marks: int = Field(..., description="Marks obtained", examples=[75])
    percentage: float = Field(..., description="Percentage score", examples=[75.0])
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {"from_attributes": True}


class AttemptSubmit(BaseModel):
    """Submit final answers for a test attempt"""
    attempt_id: int = Field(..., description="Attempt ID", examples=[1])
    answers: Dict[str, int | str] = Field(..., description="Final answers (question_id -> option_id or text)", examples=[{"1": 2, "2": "My answer"}])


class AttemptDraftSave(BaseModel):
    """Auto-save draft answers during test"""
    answers: Dict[str, int | str] = Field(..., description="Draft answers", examples=[{"1": 2, "2": "Partial answer"}])


class AttemptStats(BaseModel):
    """Student performance statistics across all attempts"""
    student_id: int = Field(..., description="Student ID", examples=[1])
    total_attempts: int = Field(..., description="Total attempts", examples=[10])
    avg_percentage: float = Field(..., description="Average percentage", examples=[78.5])
    total_time_minutes: int = Field(..., description="Total time spent", examples=[600])
    subject_wise_stats: Dict[str, dict] = Field(..., description="Subject-wise statistics", examples=[{"Physics": {"attempts": 5, "avg": 80.0}}])
