from pydantic import BaseModel, Field

from app.schemas.common import UserSummary


class ProfileResponse(UserSummary):
    is_valid: bool
    preferences: dict


class ProfileUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    middle_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    timezone: str | None = None
