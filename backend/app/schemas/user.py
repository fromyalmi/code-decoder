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
