from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Reminder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reminders"

    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(Text(), default="")
    comment: Mapped[str] = mapped_column(Text(), default="")
    type: Mapped[str] = mapped_column(String(50), default="manual")
    status: Mapped[int] = mapped_column(Integer, default=0)
    date_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    task: Mapped["Task"] = relationship(back_populates="reminders")
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assignee_id])


if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User
