# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request with email and password"""
    email: EmailStr = Field(..., description="User's email address", examples=["student@example.com"])
    password: str = Field(..., description="User's password", min_length=6, examples=["SecurePass123"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "student@example.com",
                    "password": "SecurePass123"
                }
            ]
        }
    }


class RegisterRequest(BaseModel):
    """Registration request for new student account"""
    email: EmailStr = Field(..., description="Student's email address", examples=["newstudent@example.com"])
    password: str = Field(..., description="Password (min 6 characters)", min_length=6, examples=["SecurePass123"])
    name: str = Field(..., description="Student's full name", min_length=1, examples=["Rahul Sharma"])
    class_name: int = Field(..., description="Class/Grade (8-12)", ge=8, le=12, examples=[10])
    medium: str = Field(default="English", description="Medium of instruction", examples=["English", "Hindi"])
    subjects: str = Field(default="", description="Comma-separated list of subjects", examples=["Mathematics,Physics,Chemistry"])
    board: str = Field(default="CBSE", description="Education board", examples=["CBSE", "ICSE", "State Board"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newstudent@example.com",
                    "password": "SecurePass123",
                    "name": "Rahul Sharma",
                    "class_name": 10,
                    "medium": "English",
                    "subjects": "Mathematics,Physics,Chemistry,Biology",
                    "board": "CBSE"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """JWT token response with user and student IDs"""
    access_token: str = Field(..., description="JWT access token for authentication")
    token_type: str = Field(default="Bearer", description="Token type (always Bearer)")
    user_id: int = Field(..., description="User account ID", examples=[1])
    student_id: int = Field(..., description="Student profile ID", examples=[1])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "Bearer",
                    "user_id": 1,
                    "student_id": 1
                }
            ]
        }
    }


class TokenRefreshRequest(BaseModel):
    """Token refresh request (not yet implemented)"""
    refresh_token: str = Field(..., description="Refresh token to get new access token")
