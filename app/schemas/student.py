# app/schemas/student.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StudentCreate(BaseModel):
    """Create student profile"""
    user_id: int
    name: str
    class_name: int
    medium: str = "English"
    subjects: Optional[str] = None
    school_name: Optional[str] = None
    board: str = "CBSE"


class StudentUpdate(BaseModel):
    """Update student profile"""
    name: Optional[str] = None
    class_name: Optional[int] = None
    medium: Optional[str] = None
    subjects: Optional[str] = None
    school_name: Optional[str] = None
    board: Optional[str] = None


class StudentRead(BaseModel):
    """Student profile response"""
    id: int
    user_id: int
    name: str
    class_name: int
    medium: str
    subjects: Optional[str] = None
    school_name: Optional[str] = None
    board: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
