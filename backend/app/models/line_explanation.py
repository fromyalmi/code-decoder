import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class LineExplanation(SQLModel, table=True):
    __tablename__ = "lineexplanation"
    id: Optional[int] = Field(default=None, primary_key=True)
    analysis_id: uuid.UUID = Field(foreign_key="analysis.id")
    line_no: int
    short: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
