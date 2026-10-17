from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.comment import Comment
from app.repositories.comments import CommentRepository
from app.repositories.tasks import TaskRepository


class CommentService:
    """Сервис комментариев"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.comments = CommentRepository(session)
        self.tasks = TaskRepository(session)

    async def create(
        self,
        *,
        task_id: UUID,
        created_by_id: UUID,
        body: str,
        reply_to_id: UUID | None,
        mentioned_user_ids: list[UUID],
    ) -> Comment:
        """Создаёт комментарий"""

        task = await self.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task not found.")
        comment = Comment(
            task_id=task_id,
            created_by_id=created_by_id,
            body=body,
            reply_to_id=reply_to_id,
            mentioned_user_ids=[str(item) for item in mentioned_user_ids],
        )
        await self.comments.create(comment)
        await self.session.commit()
        return comment

    async def list_by_task(self, task_id: UUID) -> list[Comment]:
        return await self.comments.list_by_task(task_id)

    async def update(self, comment_id: UUID, *, body: str) -> Comment:
        comment = await self.comments.get(comment_id)
        if not comment:
            raise NotFoundError("Comment not found.")
        comment.body = body
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def delete(self, comment_id: UUID) -> None:
        comment = await self.comments.get(comment_id)
        if not comment:
            raise NotFoundError("Comment not found.")
        comment.deleted_at = datetime.now(UTC)
        await self.session.commit()
