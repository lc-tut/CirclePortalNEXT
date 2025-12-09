"""Initialize master data."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.master import Campus, CircleCategory, CircleRole, SystemRole


async def init_master_data(session: AsyncSession) -> None:
    """Initialize master data if not exists."""
    # キャンパスマスタ
    campuses = [
        Campus(id=1, name="八王子", code="hachioji"),
        Campus(id=2, name="蒲田", code="kamata"),
    ]

    # サークルカテゴリマスタ
    categories = [
        CircleCategory(id=1, name="運動系", code="sports"),
        CircleCategory(id=2, name="文化系", code="culture"),
        CircleCategory(id=3, name="委員会", code="committee"),
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

    # データを追加 (既存チェックは ON CONFLICT DO NOTHING で対応)
    for campus in campuses:
        session.add(campus)
    for category in categories:
        session.add(category)
    for role in system_roles:
        session.add(role)
    for role in circle_roles:
        session.add(role)

    await session.commit()
