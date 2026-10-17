from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.enums import TASK_STATUS_LABELS
from app.models.task import Task
from app.repositories.common import as_string_list
from app.repositories.companies import CompanyRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository


class TaskService:
    """Сервис задач"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tasks = TaskRepository(session)
        self.projects = ProjectRepository(session)
        self.companies = CompanyRepository(session)

    async def create(
        self,
        *,
        project_id: UUID,
        creator_id: UUID,
        name: str,
        description: str,
        responsible_by_id: UUID | None,
        implement_by_id: UUID | None,
        managed_by_id: UUID | None,
        parent_task_id: UUID | None,
        tag_ids: list,
        field_values: dict,
        priority: int,
        finish_to: datetime | None,
        icon: str,
        is_epic: bool,
        watcher_ids: list[UUID],
        coworker_ids: list[UUID],
    ) -> Task:
        """Создаёт задачу"""

        project = await self.projects.get(project_id)
        if not project:
            raise NotFoundError("Project not found.")

        parent_task = None
        path: list[str] = []
        if parent_task_id:
            parent_task = await self.get(parent_task_id)
            path = [*parent_task.path, str(parent_task_id)]

        sequential_id = await self.tasks.next_sequential_id(project_id)
        people_ids = as_string_list(
            [
                creator_id,
                responsible_by_id,
                implement_by_id,
                managed_by_id,
                *watcher_ids,
                *coworker_ids,
            ],
        )

        task = Task(
            sequential_id=sequential_id,
            federation_id=project.federation_id,
            company_id=project.company_id,
            project_id=project_id,
            parent_task_id=parent_task_id,
            name=name,
            description=description,
            icon=icon,
            created_by_id=creator_id,
            responsible_by_id=responsible_by_id,
            implement_by_id=implement_by_id,
            managed_by_id=managed_by_id,
            watcher_ids=as_string_list(watcher_ids),
            coworker_ids=as_string_list(coworker_ids),
            people_ids=people_ids,
            path=path,
            is_epic=is_epic,
            field_values=field_values,
            priority=priority,
            finish_to=finish_to,
            activity_at=datetime.now(UTC),
        )

        if tag_ids:
            tag_objects = []
            for tag_id in tag_ids:
                tag = await self.companies.get_tag(tag_id)
                if tag:
                    tag_objects.append(tag)
            task.tags = tag_objects

        await self.tasks.create(task)
        task.path = [*path, str(task.id)]
        await self.session.commit()
        await self.session.refresh(task)
        return await self.get(task.id)

    async def get(self, task_id: UUID) -> Task:
        task = await self.tasks.get(task_id)
        if not task:
            raise NotFoundError("Task not found.")
        return task

    async def list(
        self,
        *,
        project_id: UUID | None = None,
        company_id: UUID | None = None,
        status: int | None = None,
        responsible_by_id: UUID | None = None,
    ) -> list[Task]:
        return await self.tasks.list(
            project_id=project_id,
            company_id=company_id,
            status=status,
            responsible_by_id=responsible_by_id,
        )

    async def update(
        self,
        task_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        responsible_by_id: UUID | None = None,
        implement_by_id: UUID | None = None,
        managed_by_id: UUID | None = None,
        status: int | None = None,
        priority: int | None = None,
        finish_to: datetime | None = None,
        icon: str | None = None,
        field_values: dict | None = None,
        watcher_ids: Sequence[UUID] | None = None,
        coworker_ids: Sequence[UUID] | None = None,
    ) -> Task:
        """Обновляет задачу"""

        task = await self.get(task_id)

        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if responsible_by_id is not None:
            task.responsible_by_id = responsible_by_id
        if implement_by_id is not None:
            task.implement_by_id = implement_by_id
        if managed_by_id is not None:
            task.managed_by_id = managed_by_id
        if priority is not None:
            task.priority = priority
        if finish_to is not None:
            task.finish_to = finish_to
        if icon is not None:
            task.icon = icon
        if field_values is not None:
            task.field_values = field_values
        if watcher_ids is not None:
            task.watcher_ids = as_string_list(watcher_ids)
        if coworker_ids is not None:
            task.coworker_ids = as_string_list(coworker_ids)
        if status is not None and status != task.status:
            task.status = status
            task.stops = [
                *task.stops,
                {
                    "status_id": status,
                    "status_name": TASK_STATUS_LABELS.get(status, "Unknown"),
                    "created_at": datetime.now(UTC).isoformat(),
                },
            ]
        task.activity_at = datetime.now(UTC)

        task.people_ids = as_string_list(
            [
                task.created_by_id,
                task.responsible_by_id,
                task.implement_by_id,
                task.managed_by_id,
                *[UUID(value) for value in task.watcher_ids],
                *[UUID(value) for value in task.coworker_ids],
            ],
        )

        await self.session.commit()
        await self.session.refresh(task)
        return await self.get(task_id)

    async def delete(self, task_id: UUID) -> None:
        task = await self.get(task_id)
        task.deleted_at = datetime.now(UTC)
        await self.session.commit()
