# app/schemas/progress.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProgressCreate(BaseModel):
    """Create progress entry"""
    student_id: int
    subject: str
    chapter: str
    class_name: int
    completion_percentage: int = Field(ge=0, le=100)
    time_spent_minutes: int = Field(ge=0, default=0)
    chunks_viewed: int = Field(ge=0, default=0)
    last_chunk_id: Optional[int] = None


class ProgressUpdate(BaseModel):
    """Update progress entry"""
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    chunks_viewed: Optional[int] = Field(None, ge=0)
    is_completed: Optional[bool] = None
    last_chunk_id: Optional[int] = None


class ProgressRead(BaseModel):
    """Progress entry response"""
    id: int
    student_id: int
    subject: str
    chapter: str
    class_name: int
    completion_percentage: int
    time_spent_minutes: int
    chunks_viewed: int
    is_completed: bool
    last_chunk_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubjectProgress(BaseModel):
    """Aggregated progress for a subject"""
    subject: str
    total_chapters: int
    completed_chapters: int
    avg_completion: float
    total_time_minutes: int


class ProgressOverview(BaseModel):
    """Overall progress overview for a student"""
    student_id: int
    subjects: list[SubjectProgress]
    total_time_minutes: int
    overall_completion: float
