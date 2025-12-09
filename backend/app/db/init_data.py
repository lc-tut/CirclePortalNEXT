"""Initialize master data."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.master import Campus, CircleRole, SystemRole


async def init_master_data(session: AsyncSession) -> None:
    """
    Initialize master data if not exists.

    Args:
        session: Database session

    Raises:
        SQLAlchemyError: If database operation fails

    Note:
        This function should be called during application startup.
        It will silently skip if master data already exists in the database.
    """
    # キャンパスマスタ
    campuses = [
        Campus(id=1, name="八王子", code="hachioji"),
        Campus(id=2, name="蒲田", code="kamata"),
    ]

    # システムロールマスタ
    system_roles = [
        SystemRole(id=1, name="SystemAdmin", code="system_admin"),
        SystemRole(id=2, name="General", code="general"),
    ]

    # サークルロールマスタ
    circle_roles = [
        CircleRole(id=1, name="Leader", code="leader", description="サークル代表(全権限)"),
        CircleRole(id=2, name="Editor", code="editor", description="幹部(編集権限あり)"),
        CircleRole(id=3, name="Member", code="member", description="平部員(閲覧のみ)"),
    ]

    # 既存データのチェック (既存チェック)
    # 各マスタテーブルが既に存在するかを確認し、存在しない場合のみ追加
    result = await session.execute(select(Campus).limit(1))
    if not result.scalar_one_or_none():
        for campus in campuses:
            session.add(campus)
        for role in system_roles:
            session.add(role)
        for role in circle_roles:
            session.add(role)
        await session.commit()
