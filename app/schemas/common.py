from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSummary(ORMModel):
    id: UUID
    first_name: str
    last_name: str
    middle_name: str
    email: str
    phone: str
    color: str
    has_photo: bool


class MessageResponse(BaseModel):
    message: str


class EntityRef(ORMModel):
    id: UUID
    name: str


class TimestampedModel(ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
