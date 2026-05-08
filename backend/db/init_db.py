from sqlalchemy import text
from backend.db.models import Base
from backend.db.session import engine


CREATE_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION chunks_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('pg_catalog.english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

DROP_TRIGGER_SQL = "DROP TRIGGER IF EXISTS tsvector_update ON chunks;"

CREATE_TRIGGER_SQL = """
CREATE TRIGGER tsvector_update
BEFORE INSERT OR UPDATE OF content
ON chunks
FOR EACH ROW
EXECUTE FUNCTION chunks_search_vector_update();
"""


BACKFILL_SQL = """
UPDATE chunks
SET search_vector = to_tsvector('pg_catalog.english', COALESCE(content, ''))
WHERE search_vector IS NULL;
"""


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(CREATE_FUNCTION_SQL))
        await conn.execute(text(DROP_TRIGGER_SQL))
        await conn.execute(text(CREATE_TRIGGER_SQL))
        # Backfill any chunks inserted before the trigger was active
        await conn.execute(text(BACKFILL_SQL))


async def close_db() -> None:
    await engine.dispose()
