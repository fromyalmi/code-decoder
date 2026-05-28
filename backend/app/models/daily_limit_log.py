import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class DailyLimitLog(SQLModel, table=True):
    __tablename__ = "dailylimitlog"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    reason: str = Field(default="analysis")
    before: int
    after: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
