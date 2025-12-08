"""Circle creation permit model."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class CircleCreationPermit(SQLModel, table=True):
    """Circle creation permit model."""

    __tablename__ = "circle_creation_permits"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    admin_memo: str = Field(default="")
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: datetime | None = Field(default=None)
