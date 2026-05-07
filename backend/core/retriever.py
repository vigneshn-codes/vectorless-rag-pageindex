from typing import List
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.query import SourceChunk

logger = logging.getLogger(__name__)

SNIPPET_LENGTH = 300

# Stage 1: strict FTS — all query words must match (stemmed)
FTS_STRICT = """
SELECT c.id, c.document_id, c.page_number, c.chunk_index, c.content, d.filename,
       ts_rank(c.search_vector, query) AS rank
FROM chunks c
JOIN documents d ON d.id = c.document_id,
     plainto_tsquery('english', :query_text) query
WHERE c.search_vector IS NOT NULL AND c.search_vector @@ query
ORDER BY rank DESC
LIMIT :limit
"""

# Stage 2: loose FTS — any query word matches (OR logic)
FTS_LOOSE = """
SELECT c.id, c.document_id, c.page_number, c.chunk_index, c.content, d.filename,
       ts_rank(c.search_vector, query) AS rank
FROM chunks c
JOIN documents d ON d.id = c.document_id,
     to_tsquery('english', :or_query) query
WHERE c.search_vector IS NOT NULL AND c.search_vector @@ query
ORDER BY rank DESC
LIMIT :limit
"""

# Stage 3: ILIKE keyword scan — no tsvector needed
ILIKE_QUERY = """
SELECT c.id, c.document_id, c.page_number, c.chunk_index, c.content, d.filename,
       1.0 AS rank
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE {conditions}
ORDER BY c.chunk_index
LIMIT :limit
"""

# Stage 4: return most recent chunks when nothing else matches
FALLBACK_QUERY = """
SELECT c.id, c.document_id, c.page_number, c.chunk_index, c.content, d.filename,
       0.0 AS rank
FROM chunks c
JOIN documents d ON d.id = c.document_id
ORDER BY c.created_at DESC
LIMIT :limit
"""


def _make_snippet(content: str, length: int = SNIPPET_LENGTH) -> str:
    content = content.strip()
    if len(content) <= length:
        return content
    return content[:length].rsplit(" ", 1)[0] + "..."


def _to_source_chunks(rows) -> List[SourceChunk]:
    return [
        SourceChunk(
            document_id=row["document_id"],
            filename=row["filename"],
            page_number=row["page_number"],
            snippet=_make_snippet(row["content"]),
            score=float(row["rank"]),
        )
        for row in rows
    ]


def _make_or_tsquery(question: str) -> str:
    stop_words = {"a", "an", "the", "is", "in", "on", "at", "of", "to", "and", "or", "for", "with", "any"}
    words = [w.strip(".,!?;:\"'()[]") for w in question.split()]
    terms = [w for w in words if len(w) > 2 and w.lower() not in stop_words]
    return " | ".join(terms) if terms else question.split()[0]


async def retrieve_chunks(
    session: AsyncSession,
    question: str,
    limit: int = 10,
) -> List[SourceChunk]:
    if not question.strip():
        return []

    # Stage 1: strict FTS
    try:
        result = await session.execute(
            text(FTS_STRICT), {"query_text": question, "limit": limit}
        )
        rows = result.mappings().all()
        if rows:
            logger.info(f"FTS strict: {len(rows)} results")
            return _to_source_chunks(rows)
    except Exception as e:
        logger.warning(f"FTS strict failed: {e}")

    # Stage 2: loose FTS (any word OR)
    try:
        or_query = _make_or_tsquery(question)
        result = await session.execute(
            text(FTS_LOOSE), {"or_query": or_query, "limit": limit}
        )
        rows = result.mappings().all()
        if rows:
            logger.info(f"FTS loose: {len(rows)} results")
            return _to_source_chunks(rows)
    except Exception as e:
        logger.warning(f"FTS loose failed: {e}")

    # Stage 3: ILIKE scan on individual keywords
    try:
        stop_words = {"a", "an", "the", "is", "in", "on", "at", "of", "to", "and", "or", "for", "with", "any", "list"}
        keywords = [
            w.strip(".,!?;:\"'()[]").lower()
            for w in question.split()
            if len(w.strip(".,!?;:\"'()[]")) > 3 and w.lower() not in stop_words
        ][:5]

        if keywords:
            conditions = " OR ".join(
                f"LOWER(c.content) LIKE :kw{i}" for i in range(len(keywords))
            )
            params: dict = {"limit": limit}
            for i, kw in enumerate(keywords):
                params[f"kw{i}"] = f"%{kw}%"

            result = await session.execute(
                text(ILIKE_QUERY.format(conditions=conditions)), params
            )
            rows = result.mappings().all()
            if rows:
                logger.info(f"ILIKE scan: {len(rows)} results")
                return _to_source_chunks(rows)
    except Exception as e:
        logger.warning(f"ILIKE scan failed: {e}")

    # Stage 4: return most recent chunks as last resort
    try:
        result = await session.execute(text(FALLBACK_QUERY), {"limit": limit})
        rows = result.mappings().all()
        if rows:
            logger.info(f"Fallback: returning {len(rows)} most recent chunks")
            return _to_source_chunks(rows)
    except Exception as e:
        logger.error(f"Fallback query failed: {e}")

    return []
