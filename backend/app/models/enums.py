"""Enum definitions."""
from enum import Enum


class CircleCategory(str, Enum):
    """サークルカテゴリ."""

    SPORTS = "sports"  # 運動系
    CULTURE = "culture"  # 文化系
    COMMITTEE = "committee"  # 委員会


class AnnouncementType(str, Enum):
    """お知らせ種別."""

    EVENT = "event"  # イベント
    NEWS = "news"  # ニュース
