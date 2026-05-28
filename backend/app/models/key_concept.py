import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class KeyConcept(SQLModel, table=True):
    __tablename__ = "keyconcept"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    analysis_id: uuid.UUID = Field(foreign_key="analysis.id")
    name: str
    definition: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
