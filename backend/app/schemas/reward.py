from datetime import date
from typing import Optional

from pydantic import BaseModel


class RewardPublic(BaseModel):
    caterpillar_balance: int
    caterpillar_total_earned: int
    caterpillar_total_spent: int
    shield_count: int
    shield_used_total: int
    streak_current: int
    streak_max: int
    streak_last_date: Optional[date]
    analysis_count_total: int


class TitleInfo(BaseModel):
    stage: int
    emoji: str
    label: str
    next_threshold: Optional[int]
