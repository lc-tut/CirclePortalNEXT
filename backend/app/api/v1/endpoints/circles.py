"""Circle endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.circle import Circle
from app.models.enums import CircleCategory
from app.services.circle import get_circles

router = APIRouter()


@router.get("", response_model=list[Circle])
async def list_circles(
    campus_id: int | None = Query(None, ge=1, le=2, description="キャンパスIDでフィルタ (1=八王子, 2=蒲田)"),
    category: CircleCategory | None = Query(None, description="カテゴリでフィルタ (sports/culture/committee)"),
    q: str | None = Query(None, description="検索キーワード (名前・説明文)"),
    limit: int = Query(20, ge=1, le=100, description="取得件数上限 (1-100、デフォルト: 20)"),
    offset: int = Query(0, ge=0, description="オフセット (デフォルト: 0)"),
    session: AsyncSession = Depends(get_session),
) -> list[Circle]:
    """
    サークル一覧を取得する.

    - 公開されているサークルのみ返す
    - 削除されたサークルは除外する
    - キャンパス・カテゴリ・キーワードでフィルタリング可能
    - limit/offset でページネーション対応
    """
    circles = await get_circles(
        session=session,
        campus_id=campus_id,
        category=category,
        search_query=q,
        limit=limit,
        offset=offset,
    )
    return circles
