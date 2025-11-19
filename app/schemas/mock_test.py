# app/schemas/mock_test.py
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class MockTestCreate(BaseModel):
    """Create mock test"""
    title: str
    description: Optional[str] = None
    subject: str
    chapter: Optional[str] = None
    class_name: int
    total_questions: int = Field(gt=0)
    total_marks: int = Field(gt=0)
    duration_minutes: int = Field(gt=0)
    passing_marks: int = Field(gt=0)
    question_ids: List[int]
    is_published: bool = False


class MockTestUpdate(BaseModel):
    """Update mock test"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None


class MockTestRead(BaseModel):
    """Mock test response"""
    id: int
    title: str
    description: Optional[str]
    subject: str
    chapter: Optional[str]
    class_name: int
    total_questions: int
    total_marks: int
    duration_minutes: int
    passing_marks: int
    question_ids: List[int]
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AttemptStart(BaseModel):
    """Start test attempt"""
    test_id: int
    student_id: int


class AttemptRead(BaseModel):
    """Test attempt response"""
    id: int
    test_id: int
    student_id: int
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    answers: Dict[str, int | str]
    questions_attempted: int
    questions_correct: int
    obtained_marks: int
    percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AttemptSubmit(BaseModel):
    """Submit test attempt"""
    attempt_id: int
    answers: Dict[str, int | str]  # question_id -> option_id or answer_text


class AttemptDraftSave(BaseModel):
    """Auto-save draft answers"""
    answers: Dict[str, int | str]


class AttemptStats(BaseModel):
    """Student's test statistics"""
    student_id: int
    total_attempts: int
    avg_percentage: float
    total_time_minutes: int
    subject_wise_stats: Dict[str, dict]
