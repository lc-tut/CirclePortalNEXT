"""Announcement model."""
from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlalchemy import Column, TIMESTAMP
from sqlmodel import Field, SQLModel

from app.models.enums import AnnouncementType


class Announcement(SQLModel, table=True):
    """
    お知らせモデル.

    サークルが発信するお知らせ情報（新歓イベント、定期公演、合宿、学祭出展等）を管理する。
    """

    __tablename__ = "announcements"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    circle_id: UUID = Field(foreign_key="circles.id", index=True)
    type: AnnouncementType = Field(index=True)
    title: str = Field(description="お知らせタイトル")
    content: str = Field(default="", description="お知らせ本文")
    # イベント情報（イベント告知の場合のみ使用）
    event_date_start: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="イベント開始日時",
    )
    event_date_end: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="イベント終了日時",
    )
    event_location: str | None = Field(default=None, description="イベント開催場所")
    # メタ情報
    is_pinned: bool = Field(default=False, description="ピン留めフラグ（重要なお知らせを上部固定）")
    published_at: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="公開日時（NULLの場合は下書き）",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(UTC),
        ),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="論理削除",
    )
