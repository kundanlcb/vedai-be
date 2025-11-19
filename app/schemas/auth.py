# app/schemas/auth.py
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request with email and password"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str
    name: str
    class_name: int
    medium: str = "English"
    subjects: str = ""  # comma-separated
    board: str = "CBSE"


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "Bearer"
    user_id: int
    student_id: int


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str
