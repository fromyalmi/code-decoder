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


class LineExplanationItem(BaseModel):
    line_no: int
    short: str


class DeepLeafItem(BaseModel):
    line_no: int
    deep: str


class KeyConceptCreateItem(BaseModel):
    name: str
    definition: str
    is_new: bool


class KeyConceptDetailItem(BaseModel):
    name: str
    definition: str


class AnalysisCreateResponse(BaseModel):
    id: str
    user_id: str
    code_original: str
    code_processed: str
    code_sha256: str
    language: str
    line_count_original: int
    line_count_processed: int
    line_mapping: dict[str, int]
    forest: str
    tree: str
    line_explanations: List[LineExplanationItem]
    deep_leaves: List[DeepLeafItem]
    tags: List[str]
    key_concepts: List[KeyConceptCreateItem]
    created_at: str
    daily_used: int
    leaf_counter: int
    is_favorite: bool
    memo: Optional[str]
    cache_hit: bool


class AnalysisDetailResponse(BaseModel):
    id: str
    user_id: str
    created_at: str
    language: str
    code_original: str
    code_processed: str
    forest: str
    tree: str
    tags: List[str]
    memo: Optional[str]
    is_favorite: bool
    line_explanations: List[LineExplanationItem]
    deep_leaves: List[DeepLeafItem]
    key_concepts: List[KeyConceptDetailItem]
