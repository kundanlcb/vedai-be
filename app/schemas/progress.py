# app/schemas/progress.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProgressCreate(BaseModel):
    """Create a new progress entry for chapter tracking"""
    student_id: int = Field(..., description="Student ID", examples=[1])
    subject: str = Field(..., description="Subject name", examples=["Physics"])
    chapter: str = Field(..., description="Chapter name", examples=["Light and Reflection"])
    class_name: int = Field(..., description="Class/Grade", ge=8, le=12, examples=[10])
    completion_percentage: int = Field(..., description="Completion percentage", ge=0, le=100, examples=[75])
    time_spent_minutes: int = Field(default=0, description="Time spent in minutes", ge=0, examples=[45])
    chunks_viewed: int = Field(default=0, description="Content chunks viewed", ge=0, examples=[12])
    last_chunk_id: Optional[int] = Field(default=None, description="Last viewed chunk ID", examples=[123])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "student_id": 1,
                    "subject": "Physics",
                    "chapter": "Light and Reflection",
                    "class_name": 10,
                    "completion_percentage": 75,
                    "time_spent_minutes": 45,
                    "chunks_viewed": 12,
                    "last_chunk_id": 123
                }
            ]
        }
    }


class ProgressUpdate(BaseModel):
    """Update existing progress entry"""
    completion_percentage: Optional[int] = Field(default=None, description="Updated completion %", ge=0, le=100, examples=[85])
    time_spent_minutes: Optional[int] = Field(default=None, description="Additional time spent", ge=0, examples=[15])
    chunks_viewed: Optional[int] = Field(default=None, description="Updated chunks viewed", ge=0, examples=[15])
    is_completed: Optional[bool] = Field(default=None, description="Mark as completed", examples=[True])
    last_chunk_id: Optional[int] = Field(default=None, description="Last viewed chunk", examples=[150])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "completion_percentage": 100,
                    "time_spent_minutes": 60,
                    "chunks_viewed": 20,
                    "is_completed": True
                }
            ]
        }
    }


class ProgressRead(BaseModel):
    """Progress entry details with timestamps"""
    id: int = Field(..., description="Progress entry ID", examples=[1])
    student_id: int = Field(..., description="Student ID", examples=[1])
    subject: str = Field(..., description="Subject", examples=["Physics"])
    chapter: str = Field(..., description="Chapter", examples=["Light and Reflection"])
    class_name: int = Field(..., description="Class", examples=[10])
    completion_percentage: int = Field(..., description="Completion %", examples=[75])
    time_spent_minutes: int = Field(..., description="Time spent", examples=[45])
    chunks_viewed: int = Field(..., description="Chunks viewed", examples=[12])
    is_completed: bool = Field(..., description="Completed status", examples=[False])
    last_chunk_id: Optional[int] = Field(default=None, description="Last chunk", examples=[123])
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")
    
    model_config = {"from_attributes": True}


class SubjectProgress(BaseModel):
    """Aggregated progress statistics for a subject"""
    subject: str = Field(..., description="Subject name", examples=["Physics"])
    total_chapters: int = Field(..., description="Total chapters", examples=[15])
    completed_chapters: int = Field(..., description="Completed chapters", examples=[10])
    avg_completion: float = Field(..., description="Average completion %", examples=[72.5])
    total_time_minutes: int = Field(..., description="Total time spent", examples=[450])


class ProgressOverview(BaseModel):
    """Overall progress overview for a student across all subjects"""
    student_id: int = Field(..., description="Student ID", examples=[1])
    subjects: list[SubjectProgress] = Field(..., description="Subject-wise progress")
    total_time_minutes: int = Field(..., description="Total time spent", examples=[1200])
    overall_completion: float = Field(..., description="Overall completion %", examples=[68.5])
