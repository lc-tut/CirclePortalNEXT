"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import circles

api_router = APIRouter()

# サークル関連エンドポイント
api_router.include_router(circles.router, prefix="/circles", tags=["circles"])
