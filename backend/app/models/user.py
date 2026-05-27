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
