import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class AnalysisCache(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    code_sha256: str = Field(max_length=64, index=True)
    result: dict = Field(sa_column=Column(JSON, nullable=False))
    expires_at: datetime
    hit_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
