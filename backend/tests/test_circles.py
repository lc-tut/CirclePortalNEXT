"""Test cases for circles endpoints."""
import os
from datetime import UTC, datetime
from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.circle import Circle
from app.models.enums import CircleCategory
from app.models.user import User


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
            deleted_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
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
        # 3つのサークルを作成 (作成順序を指定)
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

        # ORDER BY created_at DESC なので、最新作成順 (C, B, A) の順
        # 最初の2件取得 (limit=2, offset=0) - C, B
        response = await client.get("/api/v1/circles?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "サークルC"
        assert data[1]["name"] == "サークルB"

        # 次の1件取得 (limit=2, offset=2) - A
        response = await client.get("/api/v1/circles?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "サークルA"

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


class TestCreateCircle:
    """POST /api/v1/circles のテスト."""

    @pytest.mark.asyncio
    async def test_create_circle_unauthorized(self, client: AsyncClient):
        """認証なしでリクエストした場合、401 Unauthorized が返る."""
        payload = {
            "name": "LinuxClub",
            "campus_id": 1,
            "category": "culture",
            "leader_email": "taro.yamada@edu.teu.ac.jp",
        }
        # Authorization ヘッダなし
        response = await client.post("/api/v1/circles", json=payload)
        assert response.status_code == 422  # FastAPI のバリデーションエラー (ヘッダ必須)

    @pytest.mark.asyncio
    async def test_create_circle_invalid_token(self, client: AsyncClient):
        """無効な JWT トークンでリクエストした場合、401 Unauthorized が返る."""
        payload = {
            "name": "LinuxClub",
            "campus_id": 1,
            "category": "culture",
            "leader_email": "taro.yamada@edu.teu.ac.jp",
        }
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.post("/api/v1/circles", json=payload, headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_circle_insufficient_permission(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """System Admin ロールを持たないユーザーでリクエストした場合、403 Forbidden が返る."""
        # テストユーザーを作成 (System Admin でない)
        user = User(
            username="general_user",
            email="general@edu.teu.ac.jp",
            sys_role_id=2,  # general role
            auth_user_id="550e8400-e29b-41d4-a716-446655440000",
        )
        db_session.add(user)
        await db_session.commit()

        # モック JWT トークンを作成
        mock_payload = {
            "sub": "550e8400-e29b-41d4-a716-446655440000",
            "email": "general@edu.teu.ac.jp",
            "resource_access": {
                "circle-portal-backend": {
                    "roles": ["general"],  # System Admin ロールなし
                }
            },
        }

        with patch(
            "app.core.security.KeycloakJWKS.get_public_key",
            new_callable=AsyncMock,
        ) as mock_get_key, patch("app.core.security.jwt.decode") as mock_decode:
            mock_decode.return_value = mock_payload

            payload = {
                "name": "LinuxClub",
                "campus_id": 1,
                "category": "culture",
                "leader_email": "taro.yamada@edu.teu.ac.jp",
            }
            headers = {"Authorization": "Bearer mock-token"}
            response = await client.post(
                "/api/v1/circles", json=payload, headers=headers
            )
            assert response.status_code == 403
            data = response.json()
            assert "Only SystemAdmin" in data["detail"]

    @pytest.mark.asyncio
    async def test_create_circle_user_not_found(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """leader_email に対応するユーザーが見つからない場合、404 Not Found が返る."""
        # System Admin ユーザーを作成
        admin_user = User(
            username="admin",
            email="admin@lcn.ad.jp",
            sys_role_id=1,  # System Admin role
            auth_user_id="550e8400-e29b-41d4-a716-446655440001",
        )
        db_session.add(admin_user)
        await db_session.commit()

        # モック JWT トークンを作成 (System Admin)
        mock_payload = {
            "sub": "550e8400-e29b-41d4-a716-446655440001",
            "email": "admin@lcn.ad.jp",
            "resource_access": {
                "circle-portal-backend": {
                    "roles": ["system_admin"],  # System Admin ロール
                }
            },
        }

        with patch(
            "app.core.security.KeycloakJWKS.get_public_key",
            new_callable=AsyncMock,
        ) as mock_get_key, patch("app.core.security.jwt.decode") as mock_decode:
            mock_decode.return_value = mock_payload

            # leader_email に存在しないユーザーを指定
            payload = {
                "name": "LinuxClub",
                "campus_id": 1,
                "category": "culture",
                "leader_email": "nonexistent@edu.teu.ac.jp",
            }
            headers = {"Authorization": "Bearer mock-token"}
            response = await client.post(
                "/api/v1/circles", json=payload, headers=headers
            )
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_circle_success(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """正常なリクエストでサークルが作成される."""
        # System Admin ユーザーを作成
        admin_user = User(
            username="admin",
            email="admin@lcn.ad.jp",
            sys_role_id=1,  # System Admin role
            auth_user_id="550e8400-e29b-41d4-a716-446655440002",
        )
        # Leader となるユーザーを作成
        leader_user = User(
            username="taro",
            email="taro.yamada@edu.teu.ac.jp",
            sys_role_id=2,  # general role
            auth_user_id="550e8400-e29b-41d4-a716-446655440003",
        )
        db_session.add_all([admin_user, leader_user])
        await db_session.commit()

        # モック JWT トークンを作成 (System Admin)
        mock_payload = {
            "sub": "550e8400-e29b-41d4-a716-446655440002",
            "email": "admin@lcn.ad.jp",
            "resource_access": {
                "circle-portal-backend": {
                    "roles": ["system_admin"],  # System Admin ロール
                }
            },
        }

        with patch(
            "app.core.security.KeycloakJWKS.get_public_key",
            new_callable=AsyncMock,
        ) as mock_get_key, patch("app.core.security.jwt.decode") as mock_decode:
            mock_decode.return_value = mock_payload

            payload = {
                "name": "LinuxClub",
                "campus_id": 1,
                "category": "culture",
                "leader_email": "taro.yamada@edu.teu.ac.jp",
            }
            headers = {"Authorization": "Bearer mock-token"}
            response = await client.post(
                "/api/v1/circles", json=payload, headers=headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "LinuxClub"
            assert data["leader_email"] == "taro.yamada@edu.teu.ac.jp"
            assert "circle_id" in data
            assert data["message"] == "Circle created successfully"

    @pytest.mark.asyncio
    async def test_create_circle_invalid_campus_id(self, client: AsyncClient):
        """invalid campus_id (範囲外)でリクエストした場合、422 Unprocessable Entity が返る."""
        mock_payload = {
            "sub": "550e8400-e29b-41d4-a716-446655440002",
            "email": "admin@lcn.ad.jp",
            "resource_access": {
                "circle-portal-backend": {
                    "roles": ["system_admin"],
                }
            },
        }

        with patch(
            "app.core.security.KeycloakJWKS.get_public_key",
            new_callable=AsyncMock,
        ) as mock_get_key, patch("app.core.security.jwt.decode") as mock_decode:
            mock_decode.return_value = mock_payload

            # campus_id=3 (invalid)
            payload = {
                "name": "LinuxClub",
                "campus_id": 3,
                "category": "culture",
                "leader_email": "taro.yamada@edu.teu.ac.jp",
            }
            headers = {"Authorization": "Bearer mock-token"}
            response = await client.post(
                "/api/v1/circles", json=payload, headers=headers
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_circle_invalid_category(self, client: AsyncClient):
        """invalid category でリクエストした場合、422 Unprocessable Entity が返る."""
        mock_payload = {
            "sub": "550e8400-e29b-41d4-a716-446655440002",
            "email": "admin@lcn.ad.jp",
            "resource_access": {
                "circle-portal-backend": {
                    "roles": ["system_admin"],
                }
            },
        }

        with patch(
            "app.core.security.KeycloakJWKS.get_public_key",
            new_callable=AsyncMock,
        ) as mock_get_key, patch("app.core.security.jwt.decode") as mock_decode:
            mock_decode.return_value = mock_payload

            # category="invalid" (invalid)
            payload = {
                "name": "LinuxClub",
                "campus_id": 1,
                "category": "invalid_category",
                "leader_email": "taro.yamada@edu.teu.ac.jp",
            }
            headers = {"Authorization": "Bearer mock-token"}
            response = await client.post(
                "/api/v1/circles", json=payload, headers=headers
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_circle_invalid_email(self, client: AsyncClient):
        """invalid email format でリクエストした場合、422 Unprocessable Entity が返る."""
        mock_payload = {
            "sub": "550e8400-e29b-41d4-a716-446655440002",
            "email": "admin@lcn.ad.jp",
            "resource_access": {
                "circle-portal-backend": {
                    "roles": ["system_admin"],
                }
            },
        }

        with patch(
            "app.core.security.KeycloakJWKS.get_public_key",
            new_callable=AsyncMock,
        ) as mock_get_key, patch("app.core.security.jwt.decode") as mock_decode:
            mock_decode.return_value = mock_payload

            # leader_email がメールアドレス形式でない
            payload = {
                "name": "LinuxClub",
                "campus_id": 1,
                "category": "culture",
                "leader_email": "invalid-email-format",
            }
            headers = {"Authorization": "Bearer mock-token"}
            response = await client.post(
                "/api/v1/circles", json=payload, headers=headers
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_circle_missing_required_field(self, client: AsyncClient):
        """必須フィールドが欠けている場合、422 Unprocessable Entity が返る."""
        mock_payload = {
            "sub": "550e8400-e29b-41d4-a716-446655440002",
            "email": "admin@lcn.ad.jp",
            "resource_access": {
                "circle-portal-backend": {
                    "roles": ["system_admin"],
                }
            },
        }

        with patch(
            "app.core.security.KeycloakJWKS.get_public_key",
            new_callable=AsyncMock,
        ) as mock_get_key, patch("app.core.security.jwt.decode") as mock_decode:
            mock_decode.return_value = mock_payload

            # name が欠けている
            payload = {
                "campus_id": 1,
                "category": "culture",
                "leader_email": "taro.yamada@edu.teu.ac.jp",
            }
            headers = {"Authorization": "Bearer mock-token"}
            response = await client.post(
                "/api/v1/circles", json=payload, headers=headers
            )
            assert response.status_code == 422


class TestCreateCircleKeycloakIntegration:
    """ローカル Keycloak を使った統合テスト (環境変数で有効化)."""

    @pytest.mark.asyncio
    async def test_create_circle_with_real_keycloak(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """環境変数 KEYCLOAK_INTEGRATION_TEST=1 のときのみ実行し、実際の Keycloak からトークンを取得してサークル作成を確認する."""

        if os.getenv("KEYCLOAK_INTEGRATION_TEST") != "1":
            pytest.skip("KEYCLOAK_INTEGRATION_TEST が 1 でないためスキップ")

        keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        realm = os.getenv("KEYCLOAK_REALM", "CirclePortal-dev")
        client_id = os.getenv("KEYCLOAK_CLIENT_ID", "circle-portal-backend")
        client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET")
        username = os.getenv("KEYCLOAK_TEST_USERNAME")
        password = os.getenv("KEYCLOAK_TEST_PASSWORD")

        # 資格情報が無ければスキップ
        if not username or not password:
            pytest.skip("Keycloak のテストユーザー資格情報が設定されていないためスキップ")

        token_endpoint = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"

        # Keycloak からアクセストークンを取得
        try:
            async with AsyncClient() as http_client:
                data = {
                    "grant_type": "password",
                    "client_id": client_id,
                    "username": username,
                    "password": password,
                }
                if client_secret:
                    data["client_secret"] = client_secret

                token_resp = await http_client.post(token_endpoint, data=data, timeout=10)
        except Exception:
            pytest.skip("Keycloak への接続に失敗したためスキップ")

        if token_resp.status_code != 200:
            pytest.skip(f"Keycloak トークン取得に失敗: {token_resp.status_code}")

        token_json = token_resp.json()
        access_token = token_json.get("access_token")
        if not access_token:
            pytest.skip("access_token が取得できなかったためスキップ")

        # 検証無しでクレームを確認し、必要なユーザー情報をDBに投入
        claims = jwt.get_unverified_claims(access_token)
        auth_user_id = claims.get("sub")
        email = claims.get("email") or f"{username}@example.com"
        resource_roles = (
            claims.get("resource_access", {})
            .get(client_id, {})
            .get("roles", [])
        )
        realm_roles = claims.get("realm_access", {}).get("roles", [])
        roles = list(dict.fromkeys(resource_roles + realm_roles))
        if "system_admin" not in roles:
            pytest.skip("system_admin ロールを持たないトークンのためスキップ")

        # 既存ユーザーがあれば再利用、無ければ作成
        result = await db_session.execute(
            select(User).where(User.auth_user_id == auth_user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                username=username,
                email=email,
                sys_role_id=1,  # System Admin
                auth_user_id=auth_user_id,
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

        # サークル作成リクエストを実行
        circle_name = f"LinuxClub-{uuid4().hex}"
        payload = {
            "name": circle_name,
            "campus_id": 1,
            "category": "culture",
            "leader_email": email,
        }

        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/v1/circles", json=payload, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == circle_name
        assert data["leader_email"] == email
        assert data["message"] == "Circle created successfully"


