"""Database session management."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

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
        except Exception:
            # マスタデータが既に存在する場合はスキップ
            pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        yield session
