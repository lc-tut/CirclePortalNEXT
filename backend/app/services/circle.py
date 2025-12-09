"""Circle service layer."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.circle import Circle
from app.models.enums import CircleCategory


async def get_circles(
    session: AsyncSession,
    campus_id: int | None = None,
    category: CircleCategory | None = None,
    search_query: str | None = None,
) -> list[Circle]:
    """
    サークル一覧を取得する.

    Args:
        session: データベースセッション
        campus_id: キャンパスIDフィルタ (optional)
        category: カテゴリフィルタ (optional)
        search_query: 検索クエリ (optional、名前または説明文に含まれる)

    Returns:
        サークルのリスト (公開済み・削除されていないもののみ)
    """
    # 基本クエリ: 公開済み & 削除されていない
    query = select(Circle).where(Circle.is_published == True, Circle.deleted_at == None)  # noqa: E712

    # フィルタ適用
    if campus_id is not None:
        query = query.where(Circle.campus_id == campus_id)
    if category is not None:
        query = query.where(Circle.category == category)
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.where(
            (Circle.name.ilike(search_pattern)) | (Circle.description.ilike(search_pattern))
        )

    # 実行
    result = await session.execute(query)
    circles = result.scalars().all()
    return list(circles)
