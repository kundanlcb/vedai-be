# app/schemas/student.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    """Create student profile during registration"""
    user_id: int = Field(..., description="Associated user account ID", examples=[1])
    name: str = Field(..., description="Student's full name", min_length=1, examples=["Priya Patel"])
    class_name: int = Field(..., description="Class/Grade (8-12)", ge=8, le=12, examples=[10])
    medium: str = Field(default="English", description="Medium of instruction", examples=["English", "Hindi"])
    subjects: Optional[str] = Field(default=None, description="Comma-separated subjects", examples=["Mathematics,Physics,Chemistry"])
    school_name: Optional[str] = Field(default=None, description="School name", examples=["Delhi Public School"])
    board: str = Field(default="CBSE", description="Education board", examples=["CBSE", "ICSE"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 1,
                    "name": "Priya Patel",
                    "class_name": 10,
                    "medium": "English",
                    "subjects": "Mathematics,Physics,Chemistry,Biology",
                    "school_name": "Delhi Public School",
                    "board": "CBSE"
                }
            ]
        }
    }


class StudentUpdate(BaseModel):
    """Update student profile - all fields optional"""
    name: Optional[str] = Field(default=None, description="Student's full name", examples=["Updated Name"])
    class_name: Optional[int] = Field(default=None, description="Class/Grade (8-12)", ge=8, le=12, examples=[11])
    medium: Optional[str] = Field(default=None, description="Medium of instruction", examples=["Hindi"])
    subjects: Optional[str] = Field(default=None, description="Comma-separated subjects", examples=["Mathematics,Physics"])
    school_name: Optional[str] = Field(default=None, description="School name", examples=["Ryan International"])
    board: Optional[str] = Field(default=None, description="Education board", examples=["ICSE"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Priya Patel",
                    "class_name": 11,
                    "subjects": "Mathematics,Physics,Chemistry"
                }
            ]
        }
    }


class StudentRead(BaseModel):
    """Student profile response with timestamps"""
    id: int = Field(..., description="Student profile ID", examples=[1])
    user_id: int = Field(..., description="Associated user account ID", examples=[1])
    name: str = Field(..., description="Student's full name", examples=["Priya Patel"])
    class_name: int = Field(..., description="Class/Grade", examples=[10])
    medium: str = Field(..., description="Medium of instruction", examples=["English"])
    subjects: Optional[str] = Field(default=None, description="Subjects", examples=["Mathematics,Physics,Chemistry"])
    school_name: Optional[str] = Field(default=None, description="School name", examples=["Delhi Public School"])
    board: str = Field(..., description="Education board", examples=["CBSE"])
    is_active: bool = Field(..., description="Profile active status", examples=[True])
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "name": "Priya Patel",
                    "class_name": 10,
                    "medium": "English",
                    "subjects": "Mathematics,Physics,Chemistry,Biology",
                    "school_name": "Delhi Public School",
                    "board": "CBSE",
                    "is_active": True,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                }
            ]
        }
    }
