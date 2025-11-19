# app/models/progress.py
from __future__ import annotations
from datetime import datetime, UTC
from typing import Optional

from sqlmodel import SQLModel, Field


class ProgressEntry(SQLModel, table=True):
    """Student progress tracking for chapters"""
    __tablename__ = "progress_entry"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    
    # Content identifiers
    subject: str = Field(index=True)
    chapter: str = Field(index=True)
    class_name: int = Field(description="Class/Grade (8-12)")
    
    # Progress metrics
    completion_percentage: int = Field(default=0, ge=0, le=100, description="0-100%")
    time_spent_minutes: int = Field(default=0, description="Total time spent in minutes")
    chunks_viewed: int = Field(default=0, description="Number of content chunks viewed")
    
    # Status
    is_completed: bool = Field(default=False)
    last_chunk_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
