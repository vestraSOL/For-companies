from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedModel


class CommentCreateRequest(BaseModel):
    body: str = Field(min_length=2, max_length=5000)
    reply_to_id: UUID | None = None
    mentioned_user_ids: list[UUID] = []


class CommentUpdateRequest(BaseModel):
    body: str = Field(min_length=2, max_length=5000)


class CommentResponse(TimestampedModel):
    task_id: UUID
    created_by_id: UUID
    reply_to_id: UUID | None
    body: str
    mentioned_user_ids: list[str]
    likes: dict
    pin: bool
