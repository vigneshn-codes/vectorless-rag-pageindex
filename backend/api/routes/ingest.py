import json
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.db.models import Document
from backend.parsers.router import route_file, get_file_extension
from backend.core.chunker import pages_to_chunks
from backend.schemas.document import IngestResponse

logger = logging.getLogger(__name__)

router = APIRouter()

SUPPORTED_TYPES = {
    ".pdf", ".csv", ".xlsx", ".xls", ".docx", ".doc",
    ".json", ".txt", ".md", ".markdown", ".html", ".htm",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a document file: parse → chunk → bulk insert into DB.
    Supported: PDF, CSV, XLSX, XLS, DOCX, DOC, JSON, TXT, MD, HTML.
    """
    filename = file.filename or "unknown"
    ext = get_file_extension(filename)

    if ext not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_TYPES)}",
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size} bytes). Maximum is {MAX_FILE_SIZE} bytes.",
        )

    # Map extension to a clean file_type label
    file_type = ext.lstrip(".")

    # Parse the file
    try:
        pages = route_file(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Parsing failed for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")

    if not pages:
        raise HTTPException(
            status_code=422,
            detail="No content could be extracted from the uploaded file.",
        )

    # Chunk
    chunks = pages_to_chunks(pages, file_type)

    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="Could not produce any chunks from the parsed content.",
        )

    # Create Document record
    doc_id = uuid.uuid4()
    document = Document(
        id=doc_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        total_chunks=len(chunks),
    )
    db.add(document)
    await db.flush()  # get doc_id into DB without committing

    # Bulk insert chunks
    # We use raw SQL for efficiency and to trigger tsvector population via the trigger
    chunk_rows = []
    for chunk in chunks:
        chunk_rows.append(
            {
                "id": str(uuid.uuid4()),
                "document_id": str(doc_id),
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "metadata": json.dumps(chunk.metadata),
            }
        )

    await db.execute(
        text(
            """
            INSERT INTO chunks (id, document_id, page_number, chunk_index, content, metadata)
            VALUES (:id, :document_id, :page_number, :chunk_index, :content, CAST(:metadata AS jsonb))
            """
        ),
        chunk_rows,
    )

    await db.commit()

    logger.info(
        f"Ingested {filename}: {len(chunks)} chunks, doc_id={doc_id}"
    )

    return IngestResponse(
        document_id=doc_id,
        filename=filename,
        total_chunks=len(chunks),
    )
