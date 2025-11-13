# app/models/__init__.py
# Re-export models for easy imports across the app.
# Importing modules guarantees model classes are imported so SQLModel.metadata collects them.

from .user import User
from .content import ContentChunk
from .question import Question, QuestionOption, QuestionType

__all__ = [
    "User",
    "ContentChunk",
    "Question",
    "QuestionOption",
    "QuestionType",
]