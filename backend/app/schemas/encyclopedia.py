from pydantic import BaseModel


class EncyclopediaItem(BaseModel):
    name: str
    definition: str
    appearance_count: int
    first_seen_analysis_id: str
