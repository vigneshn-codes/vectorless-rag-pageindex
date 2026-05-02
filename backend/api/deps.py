from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.
    Routes are responsible for calling commit(). This dependency handles
    rollback on exception and always closes the session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
