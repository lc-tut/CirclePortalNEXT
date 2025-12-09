"""Circle model."""
from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlalchemy import Column, TIMESTAMP
from sqlmodel import Field, SQLModel


class Circle(SQLModel, table=True):
    """Circle model."""

    __tablename__ = "circles"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    name: str = Field(index=True)
    campus_id: int = Field(foreign_key="campuses.id", index=True)
    category_id: int = Field(foreign_key="circle_categories.id", index=True)
    description: str = Field(default="")
    location: str | None = Field(default=None)
    activity_detail: str | None = Field(default=None)
    logo_url: str | None = Field(default=None)
    cover_image_url: str | None = Field(default=None)
    is_published: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    deleted_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), nullable=True)
    )


class CircleMember(SQLModel, table=True):
    """Circle member relationship table."""

    __tablename__ = "circle_members"

    circle_id: UUID = Field(foreign_key="circles.id", primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="circle_roles.id", index=True)
