"""Test cases for circles endpoints."""
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.circle import Circle


class TestGetCircles:
    """GET /api/v1/circles のテスト."""

    @pytest.mark.asyncio
    async def test_get_circles_empty(self, client: AsyncClient):
        """サークルが0件の場合、空のリストが返る."""
        response = await client.get("/api/v1/circles")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_circles_returns_published_only(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """公開されているサークルのみが返される(非公開・削除済みは除外)."""
        # テストデータ作成 (マスタテーブルのIDを使用)
        # campus_id: 1=八王子, 2=蒲田
        # category_id: 1=運動系, 2=文化系, 3=委員会
        published_circle = Circle(
            name="公開サークル",
            campus_id=1,  # 八王子
            category_id=2,  # 文化系
            description="公開されているサークル",
            is_published=True,
        )
        unpublished_circle = Circle(
            name="非公開サークル",
            campus_id=2,  # 蒲田
            category_id=1,  # 運動系
            description="非公開のサークル",
            is_published=False,
        )
        deleted_circle = Circle(
            name="削除済みサークル",
            campus_id=1,  # 八王子
            category_id=3,  # 委員会
            description="削除済みのサークル",
            is_published=True,
            deleted_at=datetime.now(UTC),
        )

        db_session.add_all([published_circle, unpublished_circle, deleted_circle])
        await db_session.commit()

        # APIリクエスト
        response = await client.get("/api/v1/circles")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "公開サークル"
        assert data[0]["is_published"] is True

    @pytest.mark.asyncio
    async def test_get_circles_filters_by_campus(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """キャンパスでフィルタリングできる."""
        hachioji_circle = Circle(
            name="八王子サークル",
            campus_id=1,  # 八王子
            category_id=2,  # 文化系
            is_published=True,
        )
        kamata_circle = Circle(
            name="蒲田サークル",
            campus_id=2,  # 蒲田
            category_id=1,  # 運動系
            is_published=True,
        )

        db_session.add_all([hachioji_circle, kamata_circle])
        await db_session.commit()

        # 八王子のみ取得 (campus_id=1)
        response = await client.get("/api/v1/circles?campus_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "八王子サークル"

    @pytest.mark.asyncio
    async def test_get_circles_filters_by_category(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """カテゴリでフィルタリングできる."""
        sports_circle = Circle(
            name="運動系サークル",
            campus_id=1,  # 八王子
            category_id=1,  # 運動系
            is_published=True,
        )
        culture_circle = Circle(
            name="文化系サークル",
            campus_id=1,  # 八王子
            category_id=2,  # 文化系
            is_published=True,
        )

        db_session.add_all([sports_circle, culture_circle])
        await db_session.commit()

        # 運動系のみ取得 (category_id=1)
        response = await client.get("/api/v1/circles?category_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "運動系サークル"

    @pytest.mark.asyncio
    async def test_get_circles_search_by_keyword(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """フリーワード検索ができる."""
        linux_club = Circle(
            name="LinuxClub",
            campus_id=1,  # 八王子
            category_id=2,  # 文化系
            description="Linuxを愛するサークルです",
            is_published=True,
        )
        soccer_club = Circle(
            name="サッカー部",
            campus_id=1,  # 八王子
            category_id=1,  # 運動系
            description="サッカーを楽しむ部活です",
            is_published=True,
        )

        db_session.add_all([linux_club, soccer_club])
        await db_session.commit()

        # "Linux"で検索
        response = await client.get("/api/v1/circles?q=Linux")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "LinuxClub"
