# app/models/mock_test.py
from __future__ import annotations
from datetime import datetime, UTC
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field


class MockTest(SQLModel, table=True):
    """Mock test/exam model"""
    __tablename__ = "mock_test"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    
    # Classification
    subject: str = Field(index=True)
    chapter: Optional[str] = None
    class_name: int = Field(index=True, description="Class/Grade (8-12)")
    
    # Test configuration
    total_questions: int = Field(gt=0)
    total_marks: int = Field(gt=0)
    duration_minutes: int = Field(gt=0, description="Test duration in minutes")
    passing_marks: int = Field(gt=0)
    
    # Question references (list of question IDs as JSON)
    question_ids: List[int] = Field(sa_column=Column(JSON), default_factory=list)
    
    # Status
    is_published: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)


class AttemptStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    AUTO_SUBMITTED = "auto_submitted"
    ABANDONED = "abandoned"


class MockTestAttempt(SQLModel, table=True):
    """Student's attempt at a mock test"""
    __tablename__ = "mock_test_attempt"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    test_id: int = Field(foreign_key="mock_test.id", index=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    
    # Attempt details
    status: AttemptStatus = Field(default=AttemptStatus.IN_PROGRESS)
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    end_time: Optional[datetime] = None
    
    # Answers (JSON mapping question_id -> selected_option_id or answer_text)
    answers: dict = Field(sa_column=Column(JSON), default_factory=dict)
    
    # Results (computed after submission)
    questions_attempted: int = Field(default=0)
    questions_correct: int = Field(default=0)
    obtained_marks: int = Field(default=0)
    percentage: float = Field(default=0.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
