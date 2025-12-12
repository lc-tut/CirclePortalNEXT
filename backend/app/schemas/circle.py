"""サークル関連のスキーマ (リクエスト・レスポンス)."""
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import CircleCategory


class CircleCreateRequest(BaseModel):
    """サークル新規作成リクエストボディ."""

    name: str = Field(..., min_length=1, max_length=255, description="サークル名")
    campus_id: int = Field(..., ge=1, le=2, description="キャンパスID (1=八王子, 2=蒲田)")
    category: CircleCategory = Field(..., description="カテゴリ (sports/culture/committee)")
    leader_email: EmailStr = Field(..., description="代表者のメールアドレス")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "LinuxClub",
                "campus_id": 1,
                "category": "culture",
                "leader_email": "taro.yamada@edu.teu.ac.jp",
            }
        }


class CircleResponse(BaseModel):
    """サークル取得時のレスポンス."""

    id: UUID
    name: str
    campus_id: int
    category: CircleCategory
    description: str
    location: str | None
    activity_detail: str | None
    logo_url: str | None
    cover_image_url: str | None
    is_published: bool

    class Config:
        """Pydantic config."""

        from_attributes = True


class CircleCreateResponse(BaseModel):
    """サークル新規作成時のレスポンス."""

    circle_id: UUID
    name: str
    leader_email: str
    message: str = "Circle created successfully"

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "circle_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "LinuxClub",
                "leader_email": "taro.yamada@edu.teu.ac.jp",
                "message": "Circle created successfully",
            }
        }
