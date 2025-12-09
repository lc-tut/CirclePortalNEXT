"""Database session management."""
import logging
from collections.abc import AsyncGenerator

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables and master data."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # マスタデータの初期投入
    from app.db.init_data import init_master_data

    async with async_session() as session:
        try:
            await init_master_data(session)
        except IntegrityError:
            # マスタデータが既に存在する場合はスキップ
            logger.debug("Master data already exists in database, skipping initialization")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        yield session
