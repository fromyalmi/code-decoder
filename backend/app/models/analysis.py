import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Analysis(SQLModel, table=True):
    __tablename__ = "analysis"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    code_original: str
    code_processed: str
    code_sha256: str = Field(max_length=64, index=True)
    language: str = Field(default="python")
    line_count_original: int
    line_count_processed: int
    line_mapping: dict = Field(sa_column=Column(JSON, nullable=False))
    forest: str
    tree: str
    tags: list = Field(sa_column=Column(JSON, nullable=False), default_factory=list)
    is_favorite: bool = Field(default=False)
    memo: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
