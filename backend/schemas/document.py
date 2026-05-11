from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_size: Optional[int] = None


class DocumentRead(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: Optional[int] = None
    total_chunks: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentList(BaseModel):
    documents: list[DocumentRead]
    total: int


class IngestResponse(BaseModel):
    document_id: UUID
    filename: str
    total_chunks: int
