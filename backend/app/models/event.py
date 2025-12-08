"""Event model."""
from datetime import datetime
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    """Event model."""

    __tablename__ = "events"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    circle_id: UUID = Field(foreign_key="circles.id", index=True)
    title: str
    event_date_start: datetime
    event_date_end: datetime
    place: str
    description: str = Field(default="")
    deleted_at: datetime | None = Field(default=None)
