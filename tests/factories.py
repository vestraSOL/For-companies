from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import TASK_STATUS_LABELS, TaskStatus
from app.models.catalog import Catalog, CatalogField
from app.models.comment import Comment
from app.models.company import Company, CompanyField, CompanyMember, Tag
from app.models.federation import Federation, FederationMember
from app.models.project import Project, ProjectField, ProjectMember, ProjectStatus
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User


@dataclass(slots=True)
class SeededGraph:
    owner: User
    teammate: User
    federation: Federation
    company: Company
    company_member: CompanyMember
    tag: Tag
    company_field: CompanyField
    project: Project
    project_member: ProjectMember
    project_field: ProjectField
    task: Task
    catalog: Catalog
    catalog_field: CatalogField


async def create_user(
    session: AsyncSession,
    *,
    email: str,
    first_name: str = "Test",
    last_name: str = "User",
    middle_name: str = "",
    phone: str = "",
) -> User:
    user = User(
        email=email,
        password_hash="hashed-password",
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        phone=phone,
        is_valid=True,
        valid_at=datetime.now(UTC),
    )
    session.add(user)
    await session.flush()
    return user


async def seed_graph(session: AsyncSession) -> SeededGraph:
    owner = await create_user(
        session,
        email="owner@example.com",
        first_name="Ivan",
    )
    teammate = await create_user(
        session,
        email="teammate@example.com",
        first_name="Petr",
    )

    federation = Federation(
        name="Study Federation",
        created_by_id=owner.id,
    )
    session.add(federation)
    await session.flush()

    session.add(
        FederationMember(
            federation_id=federation.id,
            user_id=owner.id,
        ),
    )

    company = Company(
        federation_id=federation.id,
        name="Acme",
        created_by_id=owner.id,
    )
    session.add(company)
    await session.flush()

    company_member = CompanyMember(
        federation_id=federation.id,
        company_id=company.id,
        user_id=owner.id,
    )
    session.add(company_member)

    tag = Tag(
        federation_id=federation.id,
        company_id=company.id,
        created_by_id=owner.id,
        name="Backend",
        color="#111111",
    )
    company_field = CompanyField(
        company_id=company.id,
        name="Budget",
        hash="budget",
        description="Planned budget",
        icon="wallet",
        data_type=0,
        required_on_statuses=[1],
        style="primary",
    )
    session.add_all([tag, company_field])
    await session.flush()

    project = Project(
        federation_id=federation.id,
        company_id=company.id,
        created_by_id=owner.id,
        responsible_by_id=teammate.id,
        name="Launch",
        description="Main project",
        options={"status_enable": True},
        status_sort=[int(value) for value in TaskStatus],
        fields_sort=[company_field.hash],
    )
    session.add(project)
    await session.flush()

    project_member = ProjectMember(project_id=project.id, user_id=owner.id)
    project_field = ProjectField(
        project_id=project.id,
        company_field_id=company_field.id,
        required_on_statuses=[1, 2],
        style="compact",
    )
    session.add_all([project_member, project_field])
    session.add_all(
        [
            ProjectStatus(
                company_id=company.id,
                project_id=project.id,
                number=int(status),
                name=label,
                color="#000000",
                description="",
            )
            for status, label in TASK_STATUS_LABELS.items()
        ],
    )

    task = Task(
        sequential_id=10001,
        federation_id=federation.id,
        company_id=company.id,
        project_id=project.id,
        name="Root task",
        description="Seed task",
        icon="rocket",
        created_by_id=owner.id,
        responsible_by_id=teammate.id,
        implement_by_id=owner.id,
        managed_by_id=owner.id,
        watcher_ids=[str(owner.id)],
        coworker_ids=[str(teammate.id)],
        people_ids=[str(owner.id), str(teammate.id)],
        path=[],
        priority=5,
        field_values={"budget": 100},
        activity_at=datetime.now(UTC),
    )
    task.tags = [tag]
    session.add(task)
    await session.flush()
    task.path = [str(task.id)]

    catalog = Catalog(
        federation_id=federation.id,
        company_id=company.id,
        created_by_id=owner.id,
        name="Leads",
        description="Lead source catalog",
    )
    session.add(catalog)
    await session.flush()

    catalog_field = CatalogField(
        catalog_id=catalog.id,
        data_catalog_id=None,
        name="Source",
        hash="source",
        data_type=2,
    )
    session.add(catalog_field)
    await session.flush()

    return SeededGraph(
        owner=owner,
        teammate=teammate,
        federation=federation,
        company=company,
        company_member=company_member,
        tag=tag,
        company_field=company_field,
        project=project,
        project_member=project_member,
        project_field=project_field,
        task=task,
        catalog=catalog,
        catalog_field=catalog_field,
    )


async def create_comment(
    session: AsyncSession,
    *,
    task_id,
    created_by_id,
    body: str,
    created_at: datetime,
) -> Comment:
    comment = Comment(
        task_id=task_id,
        created_by_id=created_by_id,
        body=body,
        created_at=created_at,
    )
    session.add(comment)
    await session.flush()
    return comment


async def create_reminder(
    session: AsyncSession,
    *,
    task_id,
    created_by_id,
    assignee_id,
    date_from: datetime,
    description: str = "Reminder",
) -> Reminder:
    reminder = Reminder(
        task_id=task_id,
        created_by_id=created_by_id,
        assignee_id=assignee_id,
        description=description,
        comment="",
        type="manual",
        status=0,
        date_from=date_from,
    )
    session.add(reminder)
    await session.flush()
    return reminder
