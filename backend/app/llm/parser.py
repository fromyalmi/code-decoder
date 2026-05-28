from pydantic import BaseModel, Field


class _LineShort(BaseModel):
    line_no: int
    short: str


class _DeepLeaf(BaseModel):
    line_no: int
    deep: str


class _KeyConcept(BaseModel):
    name: str
    definition: str


class LLMAnalysisOutput(BaseModel):
    forest: str
    tree: str
    line_explanations: list[_LineShort]
    deep_leaves: list[_DeepLeaf] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    key_concepts: list[_KeyConcept] = Field(default_factory=list)


def parse_analysis_response(raw: dict) -> LLMAnalysisOutput:
    return LLMAnalysisOutput(**raw)
