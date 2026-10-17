from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.reminder import Reminder
from app.repositories.reminders import ReminderRepository
from app.repositories.tasks import TaskRepository


class ReminderService:
    """Сервис напоминаний"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.reminders = ReminderRepository(session)
        self.tasks = TaskRepository(session)

    async def create(
        self,
        *,
        task_id: UUID,
        created_by_id: UUID,
        assignee_id: UUID | None,
        description: str,
        comment: str,
        reminder_type: str,
        status: int,
        date_from,
        date_to,
    ) -> Reminder:
        """Создаёт напоминание"""

        task = await self.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task not found.")
        reminder = Reminder(
            task_id=task_id,
            created_by_id=created_by_id,
            assignee_id=assignee_id,
            description=description,
            comment=comment,
            type=reminder_type,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )
        await self.reminders.create(reminder)
        await self.session.commit()
        return reminder

    async def get(self, reminder_id: UUID) -> Reminder:
        reminder = await self.reminders.get(reminder_id)
        if not reminder:
            raise NotFoundError("Reminder not found.")
        return reminder

    async def list_by_task(self, task_id: UUID) -> list[Reminder]:
        return await self.reminders.list_by_task(task_id)

    async def list_for_user(self, user_id: UUID) -> list[Reminder]:
        return await self.reminders.list_by_user(user_id)

    async def update(self, reminder_id: UUID, **changes) -> Reminder:
        """Обновляет напоминание"""

        reminder = await self.get(reminder_id)
        for field, value in changes.items():
            if value is not None and hasattr(reminder, field):
                setattr(reminder, field, value)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder
