"""Test main endpoints."""
import pytest

from app.core.config import settings


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint (only available in debug mode)."""
    if settings.debug:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
    else:
        # 本番モードでは / エンドポイントは存在しない
        response = await client.get("/")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_health(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
