"""Circle endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, get_user_roles, is_system_admin
from app.db.session import get_session
from app.models.circle import Circle
from app.models.enums import CircleCategory
from app.schemas.circle import CircleCreateRequest, CircleCreateResponse
from app.services.circle import create_circle, get_circles

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

    権限: 誰でも可能
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


@router.post("", response_model=CircleCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_circle(
    request: CircleCreateRequest,
    authorization: str = Header(..., description="認証トークン (Bearer <token>)"),
    session: AsyncSession = Depends(get_session),
) -> CircleCreateResponse:
    """
    新規サークルを作成する.

    権限: System Admin のみ

    処理フロー:
    1. JWT トークンを検証し、ユーザー情報を取得
    2. ユーザーが System Admin ロールを持っているか確認
    3. leader_email からユーザーを検索 (存在しない場合は 404)
    4. サークルを作成 (初期状態: is_published=False)
    5. CircleMembers テーブルに Leader (role_id=1) として登録
    """
    # JWT 検証
    try:
        user_info = await get_current_user(authorization)
    except HTTPException as e:
        raise e

    # System Admin 権限チェック
    payload = user_info.get("payload", {})
    roles = get_user_roles(payload)

    if not is_system_admin(roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SystemAdmin can create circles",
        )

    # サークル作成 (サービス層で leader_email の検索も実施)
    try:
        new_circle = await create_circle(
            session=session,
            name=request.name,
            campus_id=request.campus_id,
            category=request.category,
            leader_email=request.leader_email,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return CircleCreateResponse(
        circle_id=new_circle.id,
        name=new_circle.name,
        leader_email=request.leader_email,
        message="Circle created successfully",
    )
