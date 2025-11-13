# app/models/content.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Text
from sqlmodel import SQLModel, Field
from pgvector.sqlalchemy import Vector


class ContentChunk(SQLModel, table=True):
    """
    Stores chunked text and its embedding vector (PGVector).
    Adjust Vector(dim) if you change embedding model.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    source_file: Optional[str] = None
    class_name: Optional[int] = Field(default=None, index=True)  # e.g. 8..12
    subject: Optional[str] = Field(default=None, index=True)
    chapter: Optional[str] = None
    page: Optional[int] = None
    text: str = Field(sa_column=Column(Text))
    # embedding column stored with PGVector. Default dim shown for all-MiniLM-L6-v2 (384)
    embedding: Optional[List[float]] = Field(sa_column=Column(Vector(384)), default=None)
    is_example: bool = Field(default=False)
    tokens: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    model_config = {"from_attributes": True}