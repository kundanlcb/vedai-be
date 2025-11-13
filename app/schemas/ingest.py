# app/schemas/ingest.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class IngestResponse(BaseModel):
    id: int
    filename: str
    status: str
    class_name: Optional[int] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    created_at: datetime
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)