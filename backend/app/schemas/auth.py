import re

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(v: str) -> str:
    v = str(v).strip().lower()
    if not _EMAIL_RE.match(v):
        raise ValueError("invalid email format")
    return v


class SignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    nickname: str = Field(min_length=2, max_length=12)
    agreed_terms: bool
    agreed_privacy: bool

    @field_validator("email", mode="before")
    @classmethod
    def validate_and_normalize_email(cls, v: str) -> str:
        return _normalize_email(v)


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()
