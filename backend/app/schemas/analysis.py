from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AnalysisCreateRequest(BaseModel):
    code: str = Field(min_length=1)
    language: Literal["python"] | None = None


class LeafExpandRequest(BaseModel):
    line_no: int


class LeafPinRequest(BaseModel):
    deep_text: str


class AnalysisPatchRequest(BaseModel):
    tags: Optional[List[str]] = None
    memo: Optional[str] = None
    is_favorite: Optional[bool] = None
