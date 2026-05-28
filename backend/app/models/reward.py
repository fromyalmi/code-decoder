import uuid
from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Reward(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)
    caterpillar_balance: int = Field(default=0)
    caterpillar_total_earned: int = Field(default=0)
    caterpillar_total_spent: int = Field(default=0)
    shield_count: int = Field(default=0)
    shield_used_total: int = Field(default=0)
    streak_current: int = Field(default=0)
    streak_max: int = Field(default=0)
    streak_last_date: Optional[date] = Field(default=None)
    analysis_count_total: int = Field(default=0)
    title_stage: int = Field(default=1)
    milestones_earned: str = Field(default="[]")
