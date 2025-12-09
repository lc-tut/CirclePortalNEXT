"""Master tables for reference data."""
from sqlmodel import Field, SQLModel


class Campus(SQLModel, table=True):
    """Campus master table."""

    __tablename__ = "campuses"

    id: int = Field(primary_key=True)
    name: str = Field(unique=True, index=True)  # 八王子, 蒲田
    code: str = Field(unique=True, index=True)  # hachioji, kamata


class CircleCategory(SQLModel, table=True):
    """Circle category master table."""

    __tablename__ = "circle_categories"

    id: int = Field(primary_key=True)
    name: str = Field(unique=True, index=True)  # 運動系, 文化系, 委員会
    code: str = Field(unique=True, index=True)  # sports, culture, committee


class SystemRole(SQLModel, table=True):
    """System role master table."""

    __tablename__ = "system_roles"

    id: int = Field(primary_key=True)
    name: str = Field(unique=True, index=True)  # SystemAdmin, General
    code: str = Field(unique=True, index=True)  # system_admin, general


class CircleRole(SQLModel, table=True):
    """Circle role master table."""

    __tablename__ = "circle_roles"

    id: int = Field(primary_key=True)
    name: str = Field(unique=True, index=True)  # Leader, Editor, Member
    code: str = Field(unique=True, index=True)  # leader, editor, member
    description: str = Field(default="")  # 権限の説明
