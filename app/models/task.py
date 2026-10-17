from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column(
        "task_id",
        PGUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        PGUUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Task(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tasks"

    sequential_id: Mapped[int | None] = mapped_column(Integer, index=True)
    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    parent_task_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"), default=None
    )
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text(), default="")
    icon: Mapped[str] = mapped_column(String(20), default="")
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    responsible_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    implement_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    managed_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    finished_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    coworker_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    watcher_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    people_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    path: Mapped[list[str]] = mapped_column(JSONB, default=list)
    is_epic: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[int] = mapped_column(Integer, default=0)
    priority: Mapped[int] = mapped_column(Integer, default=10)
    field_values: Mapped[dict] = mapped_column(JSONB, default=dict)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    task_entities: Mapped[dict] = mapped_column(JSONB, default=dict)
    stops: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finish_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped["Project"] = relationship(back_populates="tasks")
    parent_task: Mapped["Task | None"] = relationship(remote_side="Task.id")
    tags: Mapped[list["Tag"]] = relationship(secondary=task_tags)
    comments: Mapped[list["Comment"]] = relationship(back_populates="task")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="task")


if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.company import Tag
    from app.models.project import Project
    from app.models.reminder import Reminder
