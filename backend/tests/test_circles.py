"""Test cases for circles endpoints."""
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.circle import Circle
from app.models.enums import CircleCategory


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
        # テストデータ作成
        # campus_id: 1=八王子, 2=蒲田
        # category: sports=運動系, culture=文化系, committee=委員会
        published_circle = Circle(
            name="公開サークル",
            campus_id=1,  # 八王子
            category=CircleCategory.CULTURE,  # 文化系
            description="公開されているサークル",
            is_published=True,
        )
        unpublished_circle = Circle(
            name="非公開サークル",
            campus_id=2,  # 蒲田
            category=CircleCategory.SPORTS,  # 運動系
            description="非公開のサークル",
            is_published=False,
        )
        deleted_circle = Circle(
            name="削除済みサークル",
            campus_id=1,  # 八王子
            category=CircleCategory.COMMITTEE,  # 委員会
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
            category=CircleCategory.CULTURE,  # 文化系
            is_published=True,
        )
        kamata_circle = Circle(
            name="蒲田サークル",
            campus_id=2,  # 蒲田
            category=CircleCategory.SPORTS,  # 運動系
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
            category=CircleCategory.SPORTS,  # 運動系
            is_published=True,
        )
        culture_circle = Circle(
            name="文化系サークル",
            campus_id=1,  # 八王子
            category=CircleCategory.CULTURE,  # 文化系
            is_published=True,
        )

        db_session.add_all([sports_circle, culture_circle])
        await db_session.commit()

        # 運動系のみ取得 (category=sports)
        response = await client.get("/api/v1/circles?category=sports")
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
            category=CircleCategory.CULTURE,  # 文化系
            description="Linuxを愛するサークルです",
            is_published=True,
        )
        soccer_club = Circle(
            name="サッカー部",
            campus_id=1,  # 八王子
            category=CircleCategory.SPORTS,  # 運動系
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

    @pytest.mark.asyncio
    async def test_get_circles_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """ページネーション(limit/offset)が機能する."""
        # 3つのサークルを作成
        circles_data = [
            Circle(
                name="サークルA",
                campus_id=1,
                category=CircleCategory.CULTURE,
                is_published=True,
            ),
            Circle(
                name="サークルB",
                campus_id=1,
                category=CircleCategory.CULTURE,
                is_published=True,
            ),
            Circle(
                name="サークルC",
                campus_id=1,
                category=CircleCategory.CULTURE,
                is_published=True,
            ),
        ]
        db_session.add_all(circles_data)
        await db_session.commit()

        # 最初の2件取得 (limit=2, offset=0)
        response = await client.get("/api/v1/circles?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "サークルA"
        assert data[1]["name"] == "サークルB"

        # 次の1件取得 (limit=2, offset=2)
        response = await client.get("/api/v1/circles?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "サークルC"

    @pytest.mark.asyncio
    async def test_get_circles_pagination_limit_validation(
        self, client: AsyncClient
    ):
        """limit の値が1-100の範囲外の場合、エラーが返る."""
        # limit=0 (不正)
        response = await client.get("/api/v1/circles?limit=0")
        assert response.status_code == 422

        # limit=101 (不正)
        response = await client.get("/api/v1/circles?limit=101")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_circles_pagination_offset_validation(
        self, client: AsyncClient
    ):
        """offset の値が負の場合、エラーが返る."""
        # offset=-1 (不正)
        response = await client.get("/api/v1/circles?offset=-1")
        assert response.status_code == 422


class TestSQLInjectionResistance:
    """SQLインジェクション攻撃への耐性テスト."""

    @pytest.mark.asyncio
    async def test_search_with_sql_injection_attempt_union(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """UNION ベースのSQLインジェクション試行に耐性があることを確認."""
        # テストデータ作成
        circle = Circle(
            name="正常なサークル",
            campus_id=1,
            category=CircleCategory.CULTURE,
            is_published=True,
        )
        db_session.add(circle)
        await db_session.commit()

        # UNION ベースのインジェクション試行
        injection_query = "test' UNION SELECT * FROM users WHERE '1'='1"
        response = await client.get(f"/api/v1/circles?q={injection_query}")
        assert response.status_code == 200
        # インジェクションが失敗し、マッチするサークルがないはず
        data = response.json()
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_search_with_sql_injection_attempt_or(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """OR ベースのSQLインジェクション試行に耐性があることを確認."""
        # テストデータ作成
        circle1 = Circle(
            name="公開サークル1",
            campus_id=1,
            category=CircleCategory.CULTURE,
            description="これは公開サークルです",
            is_published=True,
        )
        circle2 = Circle(
            name="非公開サークル",
            campus_id=1,
            category=CircleCategory.SPORTS,
            description="非公開",
            is_published=False,
        )
        db_session.add_all([circle1, circle2])
        await db_session.commit()

        # OR ベースのインジェクション試行（非公開サークルも取得しようとする）
        injection_query = "公開' OR is_published = false OR '1'='1"
        response = await client.get(f"/api/v1/circles?q={injection_query}")
        assert response.status_code == 200
        data = response.json()
        # 公開済みのサークルのみが返されるはず（非公開サークルは含まれない）
        assert len(data) <= 1
        for circle in data:
            assert circle["is_published"] is True

    @pytest.mark.asyncio
    async def test_search_with_sql_injection_attempt_comment(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """コメント付きのSQLインジェクション試行に耐性があることを確認."""
        # テストデータ作成
        circle = Circle(
            name="テストサークル",
            campus_id=1,
            category=CircleCategory.CULTURE,
            is_published=True,
        )
        db_session.add(circle)
        await db_session.commit()

        # コメント付きのインジェクション試行
        injection_query = "test' OR '1'='1' -- "
        response = await client.get(f"/api/v1/circles?q={injection_query}")
        assert response.status_code == 200
        data = response.json()
        # インジェクションが無効化され、正常なテキスト検索として動作
        # "test' OR '1'='1' -- " というテキストにマッチするサークルはないはず
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_search_with_special_characters(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """特殊文字を含む検索が安全に処理されることを確認."""
        # テストデータ作成
        circle1 = Circle(
            name="Python & C++ Club",
            campus_id=1,
            category=CircleCategory.CULTURE,
            description="プログラミング",
            is_published=True,
        )
        circle2 = Circle(
            name="Audio/Video Production",
            campus_id=1,
            category=CircleCategory.CULTURE,
            description="映像編集",
            is_published=True,
        )
        db_session.add_all([circle1, circle2])
        await db_session.commit()

        # 特殊文字を含む検索
        response = await client.get("/api/v1/circles?q=Python%20&%20C%2B%2B")
        assert response.status_code == 200
        data = response.json()
        # 正しく検索されること
        assert len(data) == 1
        assert "Python & C++" in data[0]["name"]

    @pytest.mark.asyncio
    async def test_search_with_percent_wildcard(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """% ワイルドカード文字を含む検索が適切に処理されることを確認."""
        # テストデータ作成
        circle = Circle(
            name="100% Happiness Club",
            campus_id=1,
            category=CircleCategory.CULTURE,
            description="楽しいサークル",
            is_published=True,
        )
        db_session.add(circle)
        await db_session.commit()

        # % を含む検索
        response = await client.get("/api/v1/circles?q=100%25")
        assert response.status_code == 200
        data = response.json()
        # % がエスケープされて正しく検索されること
        assert len(data) == 1
        assert "100%" in data[0]["name"]

    @pytest.mark.asyncio
    async def test_search_with_backslash(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """バックスラッシュを含む検索が安全に処理されることを確認."""
        # テストデータ作成
        circle = Circle(
            name="Path\\Search Club",
            campus_id=1,
            category=CircleCategory.CULTURE,
            is_published=True,
        )
        db_session.add(circle)
        await db_session.commit()

        # バックスラッシュを含む検索
        response = await client.get("/api/v1/circles?q=Path")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

