# app/schemas/question.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.question import QuestionType


class OptionCreate(BaseModel):
    text: str
    is_correct: bool = False


class OptionRead(BaseModel):
    id: int
    text: str
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    text: str
    question_type: QuestionType
    marks: Optional[int] = 1
    year: Optional[int] = None
    source_board: Optional[str] = None
    chapter: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    generated: bool = False
    options: Optional[List[OptionCreate]] = None


class QuestionRead(BaseModel):
    id: int
    text: str
    question_type: QuestionType
    marks: Optional[int]
    year: Optional[int]
    source_board: Optional[str]
    chapter: Optional[str]
    subject: Optional[str]
    difficulty: Optional[str]
    generated: bool
    options: Optional[List[OptionRead]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)