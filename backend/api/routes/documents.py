import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.db.models import Document
from backend.schemas.document import DocumentRead, DocumentList

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/documents", response_model=DocumentList)
async def list_documents(db: AsyncSession = Depends(get_db)):
    """Return all documents ordered by creation date (newest first)."""
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return DocumentList(
        documents=[DocumentRead.model_validate(doc) for doc in documents],
        total=len(documents),
    )


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and all its chunks (cascade)."""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    await db.delete(document)
    await db.commit()

    logger.info(f"Deleted document {document_id}")
    return Response(status_code=204)
