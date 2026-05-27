from typing import Optional

from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    level: Optional[int] = Field(default=None, ge=1, le=4)
