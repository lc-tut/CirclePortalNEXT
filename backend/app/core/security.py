"""セキュリティ関連の処理 (JWT検証、認証認可)."""
import asyncio
import json
from functools import lru_cache

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt
from jose.exceptions import JWTClaimsError

from app.core.config import settings


class KeycloakJWKS:
    """Keycloak の公開鍵セット (JWKS) をキャッシュして管理."""

    _keys: dict | None = None

    @classmethod
    async def get_keys(cls) -> dict:
        """Keycloak の JWKS エンドポイントから公開鍵を取得・キャッシュ."""
        if cls._keys is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/certs",
                    timeout=10.0,
                )
                response.raise_for_status()
                cls._keys = response.json()
        return cls._keys

    @classmethod
    def get_public_key(cls, token: str) -> str:
        """JWT のヘッダから kid (Key ID) を取得し、対応する公開鍵を返す."""
        try:
            unverified_header = jwt.get_unverified_header(token)
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
            ) from e

        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID",
            )

        # 同期的に JWKS を取得 (既にキャッシュされているはず)
        keys = asyncio.run(cls.get_keys())
        for key in keys.get("keys", []):
            if key.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid key ID in token",
        )


async def get_current_user(authorization: str) -> dict:
    """
    Authorization ヘッダから JWT を抽出し、検証してユーザー情報を取得.

    Args:
        authorization: Authorization ヘッダの値 ("Bearer <token>" 形式)

    Returns:
        JWT の Payload (user_id, email, roles 等を含む)

    Raises:
        HTTPException: 認証失敗時 (401 Unauthorized)
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization.split(" ", 1)[1]

    try:
        # 公開鍵を使用して JWT を検証
        public_key = KeycloakJWKS.get_public_key(token)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # audience 検証はスキップ (オプション)
        )

        user_id: str | None = payload.get("sub")
        email: str | None = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )

        return {
            "user_id": user_id,
            "email": email,
            "payload": payload,
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        ) from e


def get_user_roles(payload: dict) -> list[str]:
    """JWT Payload からユーザーのロール (Role) を抽出.

    Keycloak の resource_access 構造から circle-portal-backend クライアント
    に関連するロールを取得する.
    """
    resource_access = payload.get("resource_access", {})
    client_roles = resource_access.get(settings.keycloak_client_id, {})
    return client_roles.get("roles", [])


def is_system_admin(roles: list[str]) -> bool:
    """ユーザーが system_admin ロールを持っているか判定."""
    return "system_admin" in roles
