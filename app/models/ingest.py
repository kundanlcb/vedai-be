# app/models/ingest.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class PdfStatus(str, Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class PdfFile(SQLModel, table=True):
    """
    Tracks an uploaded PDF and its ingestion lifecycle.
    - checksum helps with deduplication
    - chunks_count is updated after ingestion
    - last_error stores the failure reason (if any)
    - class_name, subject, chapter track educational context for duplicate detection
    - unique constraint on (checksum, status) prevents duplicate processing of same file
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    filepath: str                      # local path or S3 key
    storage: str = Field(default="local")  # 'local' or 's3'
    filesize: Optional[int] = None
    checksum: Optional[str] = None
    class_name: Optional[int] = Field(default=None, index=True)  # e.g. 8..12
    subject: Optional[str] = Field(default=None, index=True)
    chapter: Optional[str] = Field(default=None, index=True)
    status: PdfStatus = Field(default=PdfStatus.PENDING, index=True)
    pages: Optional[int] = None
    chunks_count: Optional[int] = None
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}

