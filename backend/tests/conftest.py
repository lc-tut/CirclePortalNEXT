"""Test configuration."""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.db.init_data import init_master_data
from app.db.session import get_session
from app.main import app

# テスト用データベースURL (環境変数で上書き可能)
import os

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://circleportal:circleportal@localhost:5432/circleportal_test"
)


@pytest.fixture(scope="function")
async def test_engine():
    """テスト用エンジンを各テストで作成."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # テストごとに接続を作り直す
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine):
    """テスト用データベースセッション (各テストで初期化)."""
    # テーブル作成
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # セッション作成
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # マスタデータを初期化
        await init_master_data(session)
        yield session

    # テーブル削除
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def client(db_session):
    """テストクライアントを作成 (テスト用DBセッションを使用)."""

    async def get_test_session():
        yield db_session

    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
