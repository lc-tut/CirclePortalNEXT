"""Circle creation permit model."""
from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlalchemy import Column, TIMESTAMP
from sqlmodel import Field, SQLModel


class CircleCreationPermit(SQLModel, table=True):
    """Circle creation permit model."""

    __tablename__ = "circle_creation_permits"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    email: str = Field(unique=True, index=True)
    admin_memo: str = Field(default="")
    is_used: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    used_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), nullable=True)
    )
