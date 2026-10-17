from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedModel


class ReminderCreateRequest(BaseModel):
    description: str = ""
    comment: str = ""
    assignee_id: UUID | None = None
    type: str = Field(default="manual", min_length=1, max_length=50)
    status: int = 0
    date_from: datetime | None = None
    date_to: datetime | None = None


class ReminderUpdateRequest(BaseModel):
    description: str | None = None
    comment: str | None = None
    assignee_id: UUID | None = None
    type: str | None = Field(default=None, min_length=1, max_length=50)
    status: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class ReminderStatusUpdateRequest(BaseModel):
    status: int


class ReminderResponse(TimestampedModel):
    task_id: UUID
    created_by_id: UUID
    assignee_id: UUID | None
    description: str
    comment: str
    type: str
    status: int
    date_from: datetime | None
    date_to: datetime | None
