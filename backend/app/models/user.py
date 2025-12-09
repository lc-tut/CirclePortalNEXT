"""User model."""
from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlalchemy import Column, TIMESTAMP
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    sys_role_id: int = Field(foreign_key="system_roles.id", index=True)
    auth_user_id: str | None = Field(default=None, unique=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
