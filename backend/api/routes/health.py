from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Return API health status, DB connectivity, and document/chunk counts."""
    db_connected = False
    document_count = 0
    chunk_count = 0

    try:
        result = await db.execute(
            text("SELECT COUNT(*) FROM documents")
        )
        document_count = result.scalar() or 0

        result = await db.execute(
            text("SELECT COUNT(*) FROM chunks")
        )
        chunk_count = result.scalar() or 0

        db_connected = True
    except Exception:
        db_connected = False

    return {
        "status": "ok" if db_connected else "degraded",
        "db_connected": db_connected,
        "document_count": document_count,
        "chunk_count": chunk_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
