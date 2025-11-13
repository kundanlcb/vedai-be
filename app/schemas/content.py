# app/schemas/content.py
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChunkCreate(BaseModel):
    source_file: Optional[str] = None
    class_name: Optional[int] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    page: Optional[int] = None
    text: str


class ChunkRead(BaseModel):
    id: int
    source_file: Optional[str]
    class_name: Optional[int]
    subject: Optional[str]
    chapter: Optional[str]
    page: Optional[int]
    text: str
    is_example: bool
    tokens: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)