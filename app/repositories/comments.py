from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.repositories.common import active


class CommentRepository:
    """Репозиторий комментариев"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()
        await self.session.refresh(comment)
        return comment

    async def get(self, comment_id: UUID) -> Comment | None:
        query = active(select(Comment), Comment).where(Comment.id == comment_id)
        return await self.session.scalar(query)

    async def list_by_task(self, task_id: UUID) -> list[Comment]:
        """Возвращает комментарии задачи"""

        query = (
            active(select(Comment), Comment)
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())
        )
        result = await self.session.scalars(query)
        return list(result)
