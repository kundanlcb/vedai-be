# app/models/student.py
from __future__ import annotations
from datetime import datetime, UTC
from typing import Optional

from sqlmodel import SQLModel, Field


class Student(SQLModel, table=True):
    """Student profile model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    
    # Basic profile
    name: str
    class_name: int = Field(description="Class/Grade (8-12)")
    medium: str = Field(default="English", description="Medium of instruction")
    
    # Subjects (comma-separated for simplicity, can be normalized later)
    subjects: Optional[str] = Field(default=None, description="Comma-separated subject list")
    
    # Optional fields
    school_name: Optional[str] = None
    board: Optional[str] = Field(default="CBSE", description="Educational board (CBSE, ICSE, State)")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    
    # Status
    is_active: bool = Field(default=True)
