from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.comment import CommentResponse
from app.schemas.common import TimestampedModel
from app.schemas.reminder import ReminderResponse


class TaskCreateRequest(BaseModel):
    project_id: UUID
    name: str = Field(min_length=3, max_length=120)
    description: str = ""
    responsible_by_id: UUID | None = None
    implement_by_id: UUID | None = None
    managed_by_id: UUID | None = None
    parent_task_id: UUID | None = None
    tag_ids: list[UUID] = []
    field_values: dict = {}
    priority: int = 10
    finish_to: datetime | None = None
    icon: str = ""
    is_epic: bool = False
    watcher_ids: list[UUID] = []
    coworker_ids: list[UUID] = []


class TaskUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = None
    responsible_by_id: UUID | None = None
    implement_by_id: UUID | None = None
    managed_by_id: UUID | None = None
    status: int | None = None
    priority: int | None = None
    finish_to: datetime | None = None
    icon: str | None = None
    field_values: dict | None = None
    watcher_ids: list[UUID] | None = None
    coworker_ids: list[UUID] | None = None


class TaskResponse(TimestampedModel):
    sequential_id: int | None
    federation_id: UUID
    company_id: UUID
    project_id: UUID
    parent_task_id: UUID | None
    name: str
    description: str
    icon: str
    created_by_id: UUID
    responsible_by_id: UUID | None
    implement_by_id: UUID | None
    managed_by_id: UUID | None
    finished_by_id: UUID | None
    coworker_ids: list[str]
    watcher_ids: list[str]
    people_ids: list[str]
    path: list[str]
    is_epic: bool
    status: int
    priority: int
    field_values: dict
    meta: dict
    task_entities: dict
    stops: list[dict]
    activity_at: datetime | None
    finish_to: datetime | None
    finished_at: datetime | None
    tags: list[UUID]
    comments: list[CommentResponse]
    reminders: list[ReminderResponse]

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> Any:
        if not isinstance(value, list):
            return value
        return [item.id if hasattr(item, "id") else item for item in value]
