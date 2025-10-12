"""
Message schemas for API responses.
"""

from pydantic import BaseModel


class Msg(BaseModel):
    """Message schema for API responses."""

    detail: str


class MsgWithCount(Msg):
    """Message schema with count for API responses."""

    count: int
