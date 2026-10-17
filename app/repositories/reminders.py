from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder
from app.repositories.common import active


class ReminderRepository:
    """Репозиторий напоминаний"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, reminder: Reminder) -> Reminder:
        self.session.add(reminder)
        await self.session.flush()
        await self.session.refresh(reminder)
        return reminder

    async def get(self, reminder_id: UUID) -> Reminder | None:
        query = active(select(Reminder), Reminder).where(Reminder.id == reminder_id)
        return await self.session.scalar(query)

    async def list_by_task(self, task_id: UUID) -> list[Reminder]:
        query = active(select(Reminder), Reminder).where(Reminder.task_id == task_id)
        query = query.order_by(
            Reminder.date_from.asc().nullslast(), Reminder.created_at.desc()
        )
        result = await self.session.scalars(query)
        return list(result)

    async def list_by_user(self, user_id: UUID) -> list[Reminder]:
        """Возвращает напоминания пользователя"""

        query = active(select(Reminder), Reminder).where(
            or_(Reminder.assignee_id == user_id, Reminder.created_by_id == user_id),
        )
        query = query.order_by(
            Reminder.date_from.asc().nullslast(), Reminder.created_at.desc()
        )
        result = await self.session.scalars(query)
        return list(result)
