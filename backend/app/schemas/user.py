from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    level: Optional[int] = Field(default=None, ge=1, le=4)
    first_login_completed: Optional[bool] = None
    sound_enabled: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str
    level: int
    level_auto: bool
    first_login_completed_at: Optional[datetime]
    sound_enabled: bool
    daily_used: int
    daily_limit: int
    daily_remaining: int
    leaf_counter: int


class TitleInfo(BaseModel):
    stage: int
    emoji: str
    label: str
    next_threshold: Optional[int]


class RewardPublic(BaseModel):
    caterpillar_balance: int
    caterpillar_total_earned: int
    caterpillar_total_spent: int
    shield_count: int
    shield_used_total: int
    streak_current: int
    streak_max: int
    streak_last_date: Optional[str]
    analysis_count_total: int


class MeResponse(BaseModel):
    id: str
    email: str
    nickname: str
    level: int
    level_auto: bool
    first_login_completed_at: Optional[str]
    sound_enabled: bool
    daily_used: int
    daily_limit: int
    daily_remaining: int
    leaf_counter: int
    reward: RewardPublic
    title: TitleInfo
