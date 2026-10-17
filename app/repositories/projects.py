from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectField, ProjectMember, ProjectStatus
from app.repositories.common import active


class ProjectRepository:
    """Репозиторий проектов"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def get(self, project_id: UUID) -> Project | None:
        """Возвращает проект по идентификатору"""

        query = (
            active(select(Project), Project)
            .where(Project.id == project_id)
            .execution_options(populate_existing=True)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.field_links).selectinload(
                    ProjectField.company_field
                ),
                selectinload(Project.statuses),
            )
        )
        return await self.session.scalar(query)

    async def list_by_company(self, company_id: UUID) -> list[Project]:
        query = (
            active(select(Project), Project)
            .where(Project.company_id == company_id)
            .execution_options(populate_existing=True)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.field_links).selectinload(
                    ProjectField.company_field
                ),
                selectinload(Project.statuses),
            )
            .order_by(Project.created_at.desc())
        )
        result = await self.session.scalars(query)
        return list(result.unique())

    async def find_by_name(self, company_id: UUID, name: str) -> Project | None:
        query = active(select(Project), Project).where(
            Project.company_id == company_id,
            Project.name == name,
        )
        return await self.session.scalar(query)

    async def add_member(self, member: ProjectMember) -> ProjectMember:
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def get_member(self, project_id: UUID, user_id: UUID) -> ProjectMember | None:
        query = active(select(ProjectMember), ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        return await self.session.scalar(query)

    async def add_field_link(self, project_field: ProjectField) -> ProjectField:
        self.session.add(project_field)
        await self.session.flush()
        await self.session.refresh(project_field)
        return project_field

    async def get_field_link(
        self, project_id: UUID, company_field_id: UUID
    ) -> ProjectField | None:
        query = active(select(ProjectField), ProjectField).where(
            ProjectField.project_id == project_id,
            ProjectField.company_field_id == company_field_id,
        )
        return await self.session.scalar(query)

    async def add_statuses(self, statuses: Sequence[ProjectStatus]) -> None:
        self.session.add_all(list(statuses))
        await self.session.flush()
