"""Circle service layer."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.circle import Circle, CircleMember
from app.models.enums import CircleCategory
from app.models.user import User


async def get_circles(
    session: AsyncSession,
    campus_id: int | None = None,
    category: CircleCategory | None = None,
    search_query: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Circle]:
    """
    サークル一覧を取得する.

    Args:
        session: データベースセッション
        campus_id: キャンパスIDフィルタ (optional)
        category: カテゴリフィルタ (optional)
        search_query: 検索クエリ (optional、名前または説明文に含まれる)
        limit: 取得件数上限 (デフォルト: 20)
        offset: オフセット (デフォルト: 0)

    Returns:
        サークルのリスト (公開済み・削除されていないもののみ)
    """
    # 基本クエリ: 公開済み & 削除されていない
    query = select(Circle).where(Circle.is_published.is_(True), Circle.deleted_at.is_(None))

    # フィルタ適用
    if campus_id is not None:
        query = query.where(Circle.campus_id == campus_id)
    if category is not None:
        query = query.where(Circle.category == category)
    if search_query:
        # SQL LIKE のワイルドカード文字 (%, _) をエスケープ
        search_escaped = search_query.replace("%", r"\%").replace("_", r"\_")
        search_pattern = f"%{search_escaped}%"
        query = query.where(
            (Circle.name.ilike(search_pattern, escape="\\")) | 
            (Circle.description.ilike(search_pattern, escape="\\"))
        )

    # ソート適用 (作成日時の新しい順)
    query = query.order_by(Circle.created_at.desc())

    # ページネーション適用
    query = query.limit(limit).offset(offset)

    # 実行
    result = await session.execute(query)
    circles = result.scalars().all()
    return list(circles)


async def create_circle(
    session: AsyncSession,
    name: str,
    campus_id: int,
    category: CircleCategory,
    leader_email: str,
) -> Circle:
    """
    新規サークルを作成する.

    要件:
    - System Admin のみが実行可能
    - leader_email に対応するユーザーを検索し、存在しない場合は 404 を返す
    - サークルを作成（初期状態: is_published=False）
    - CircleMembers に Leader ロール (role_id=1) で登録

    Args:
        session: データベースセッション
        name: サークル名
        campus_id: キャンパスID (1=八王子, 2=蒲田)
        category: カテゴリ (sports/culture/committee)
        leader_email: 代表者のメールアドレス

    Returns:
        作成されたサークル

    Raises:
        ValueError: leader_email に対応するユーザーが見つからない場合
    """
    # leader_email からユーザーを検索
    user_query = select(User).where(User.email == leader_email)
    result = await session.execute(user_query)
    leader_user = result.scalar_one_or_none()

    if not leader_user:
        raise ValueError(f"User with email '{leader_email}' not found")

    # サークルを作成 (初期状態: is_published=False)
    new_circle = Circle(
        name=name,
        campus_id=campus_id,
        category=category,
        description="",  # 初期値は空
        is_published=False,
    )
    session.add(new_circle)
    await session.flush()  # ID を生成するため flush (commit ではなく)

    # CircleMembers に Leader ロール (role_id=1) で登録
    circle_member = CircleMember(
        circle_id=new_circle.id,
        user_id=leader_user.id,
        role_id=1,  # Leader role
    )
    session.add(circle_member)
    await session.commit()

    return new_circle

