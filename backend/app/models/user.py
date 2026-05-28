import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    nickname: str
    login_failed_count: int = Field(default=0)
    login_locked_until: Optional[datetime] = Field(default=None)
    level: int = Field(default=1)
    level_auto: bool = Field(default=False)
    first_login_completed_at: Optional[datetime] = Field(default=None)
    sound_enabled: bool = Field(default=False)
    daily_used: int = Field(default=0)
    daily_limit: int = Field(default=10)
