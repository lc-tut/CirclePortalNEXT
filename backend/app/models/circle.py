"""Circle model."""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Campus(str, Enum):
    """Campus enum."""

    HACHIOJI = "八王子"
    KAMATA = "蒲田"


class CircleCategory(str, Enum):
    """Circle category enum."""

    SPORTS = "運動系"
    CULTURE = "文化系"
    COMMITTEE = "委員会"


class CircleRole(str, Enum):
    """Circle role enum."""

    LEADER = "Leader"
    MEMBER = "Member"


class Circle(SQLModel, table=True):
    """Circle model."""

    __tablename__ = "circles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    campus: Campus
    category: CircleCategory
    description: str = Field(default="")
    location: str | None = Field(default=None)
    activity_detail: str | None = Field(default=None)
    logo_url: str | None = Field(default=None)
    cover_image_url: str | None = Field(default=None)
    is_published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = Field(default=None)


class CircleMember(SQLModel, table=True):
    """Circle member relationship table."""

    __tablename__ = "circle_members"

    circle_id: UUID = Field(foreign_key="circles.id", primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    role: CircleRole = Field(default=CircleRole.MEMBER)
