from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceChunk(BaseModel):
    document_id: UUID
    filename: str
    page_number: Optional[int] = None
    snippet: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    model: str
    usage: dict
