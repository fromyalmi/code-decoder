from typing import Literal

from pydantic import BaseModel, Field


class AnalysisCreateRequest(BaseModel):
    code: str = Field(min_length=1)
    language: Literal["python"] | None = None
