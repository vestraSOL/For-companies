from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.enums import TASK_STATUS_LABELS, TaskStatus
from app.models.project import Project, ProjectField, ProjectMember, ProjectStatus
from app.repositories.companies import CompanyRepository
from app.repositories.projects import ProjectRepository
from app.repositories.users import UserRepository


class ProjectService:
    """Сервис проектов"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.projects = ProjectRepository(session)
        self.companies = CompanyRepository(session)
        self.users = UserRepository(session)

    async def create(
        self,
        *,
        company_id: UUID,
        creator_id: UUID,
        name: str,
        description: str,
        responsible_by_id: UUID | None,
        status_sort: list[int] | None,
        fields_sort: list[str] | None,
    ) -> Project:
        """Создаёт проект"""

        company = await self.companies.get(company_id)
        if not company:
            raise NotFoundError("Company not found.")
        existing = await self.projects.find_by_name(company_id, name)
        if existing:
            raise ConflictError("Project with this name already exists.")

        project = Project(
            federation_id=company.federation_id,
            company_id=company_id,
            created_by_id=creator_id,
            responsible_by_id=responsible_by_id,
            name=name,
            description=description,
            options={
                "status_enable": True,
                "require_cancelation_comment": False,
                "require_done_comment": False,
                "color": "#000000",
            },
            status_sort=status_sort or [int(value) for value in TaskStatus],
            fields_sort=fields_sort or [],
        )
        await self.projects.create(project)
        await self.projects.add_member(
            ProjectMember(project_id=project.id, user_id=creator_id)
        )
        await self.projects.add_statuses(
            [
                ProjectStatus(
                    company_id=company_id,
                    project_id=project.id,
                    number=int(status),
                    name=label,
                    color="#000000" if status != TaskStatus.UNKNOWN else "#9ca3af",
                    description="",
                )
                for status, label in TASK_STATUS_LABELS.items()
            ],
        )
        await self.session.commit()
        return await self.get(project.id)

    async def get(self, project_id: UUID) -> Project:
        project = await self.projects.get(project_id)
        if not project:
            raise NotFoundError("Project not found.")
        return project

    async def list_by_company(self, company_id: UUID) -> list[Project]:
        return await self.projects.list_by_company(company_id)

    async def update(
        self,
        project_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        responsible_by_id: UUID | None = None,
        status_sort: list[int] | None = None,
        fields_sort: list[str] | None = None,
    ) -> Project:
        """Обновляет проект"""

        project = await self.get(project_id)
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if responsible_by_id is not None:
            project.responsible_by_id = responsible_by_id
        if status_sort is not None:
            project.status_sort = status_sort
        if fields_sort is not None:
            project.fields_sort = fields_sort
        await self.session.commit()
        await self.session.refresh(project)
        return await self.get(project_id)

    async def add_member(self, project_id: UUID, user_id: UUID) -> Project:
        project = await self.get(project_id)
        user = await self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        existing = await self.projects.get_member(project_id, user_id)
        if existing:
            raise ConflictError("User is already a project member.")
        await self.projects.add_member(
            ProjectMember(project_id=project.id, user_id=user_id)
        )
        await self.session.commit()
        return await self.get(project_id)

    async def add_field_link(
        self,
        project_id: UUID,
        *,
        company_field_id: UUID,
        required_on_statuses: list[int],
        style: str,
    ) -> Project:
        """Привязывает поле к проекту"""

        project = await self.get(project_id)
        existing = await self.projects.get_field_link(project_id, company_field_id)
        if existing:
            raise ConflictError("Field is already attached to the project.")
        await self.projects.add_field_link(
            ProjectField(
                project_id=project.id,
                company_field_id=company_field_id,
                required_on_statuses=required_on_statuses,
                style=style,
            ),
        )
        await self.session.commit()
        return await self.get(project_id)
