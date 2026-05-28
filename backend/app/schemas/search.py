from pydantic import BaseModel


class SearchResultItem(BaseModel):
    id: str
    created_at: str
    language: str
    code_preview: str
    tags: list
    matched_field: str
