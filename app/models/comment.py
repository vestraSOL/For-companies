from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Comment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "comments"

    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    reply_to_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("comments.id", ondelete="SET NULL")
    )
    body: Mapped[str] = mapped_column(Text())
    mentioned_user_ids: Mapped[list[str]] = mapped_column(JSONB, default=list)
    likes: Mapped[dict] = mapped_column(JSONB, default=dict)
    pin: Mapped[bool] = mapped_column(Boolean, default=False)

    task: Mapped["Task"] = relationship(back_populates="comments")
    created_by: Mapped["User"] = relationship()
    reply_to: Mapped["Comment | None"] = relationship(remote_side="Comment.id")


if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User
