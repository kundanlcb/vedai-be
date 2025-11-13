# app/models/question.py

from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field, Relationship


class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    NUMERICAL = "numerical"


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(sa_column=Column(Text))
    # Explicit SQLAlchemy Enum column to avoid SQLModel type inference issues
    question_type: QuestionType = Field(
        sa_column=Column(SQLEnum(QuestionType, name="question_type_enum"), nullable=False),
        default=QuestionType.MCQ,
    )
    marks: Optional[int] = Field(default=1)
    year: Optional[int] = None
    source_board: Optional[str] = None
    chapter: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    generated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship: use SQLModel Relationship to avoid SQLModel field inference issues
    options: List["QuestionOption"] = Relationship(
        back_populates="question",
        sa_relationship=relationship(
            lazy="selectin",
            cascade="all, delete-orphan",
        ),
    )


class QuestionOption(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: Optional[int] = Field(default=None, foreign_key="question.id", index=True)
    text: str = Field(sa_column=Column(Text))
    is_correct: bool = Field(default=False)

    # backref (single)
    question: Optional["Question"] = Relationship(
        back_populates="options",
        # Avoid SAWarning about overlapping copy of question_id
        sa_relationship=relationship(lazy="selectin", overlaps="options"),
    )