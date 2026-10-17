from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.repositories.common import active


class TaskRepository:
    """Репозиторий задач"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def next_sequential_id(self, project_id: UUID) -> int:
        """Возвращает следующий порядковый номер задачи"""

        query = select(func.max(Task.sequential_id)).where(
            Task.project_id == project_id,
            Task.deleted_at.is_(None),
        )
        last_value = await self.session.scalar(query)
        return (last_value or 10_000) + 1

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get(self, task_id: UUID) -> Task | None:
        query = (
            active(select(Task), Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.tags),
                selectinload(Task.comments),
                selectinload(Task.reminders),
            )
        )
        return await self.session.scalar(query)

    async def list(
        self,
        *,
        project_id: UUID | None = None,
        company_id: UUID | None = None,
        status: int | None = None,
        responsible_by_id: UUID | None = None,
    ) -> list[Task]:
        """Возвращает список задач"""

        query = active(select(Task), Task).options(
            selectinload(Task.tags),
            selectinload(Task.comments),
            selectinload(Task.reminders),
        )
        if project_id:
            query = query.where(Task.project_id == project_id)
        if company_id:
            query = query.where(Task.company_id == company_id)
        if status is not None:
            query = query.where(Task.status == status)
        if responsible_by_id:
            query = query.where(Task.responsible_by_id == responsible_by_id)
        query = query.order_by(
            Task.activity_at.desc().nullslast(), Task.created_at.desc()
        )
        result = await self.session.scalars(query)
        return list(result.unique())
