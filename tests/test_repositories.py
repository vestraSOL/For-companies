from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models.catalog import CatalogRecord
from app.models.task import Task
from app.models.user import User
from app.repositories.catalogs import CatalogRepository
from app.repositories.comments import CommentRepository
from app.repositories.companies import CompanyRepository
from app.repositories.federations import FederationRepository
from app.repositories.projects import ProjectRepository
from app.repositories.reminders import ReminderRepository
from app.repositories.tasks import TaskRepository
from app.repositories.users import UserRepository
from tests.factories import create_comment, create_reminder, seed_graph


@pytest.mark.asyncio
async def test_user_repository_search_matches_fields_and_skips_deleted(
    db_session,
) -> None:
    repository = UserRepository(db_session)

    active_user = await repository.create(
        User(
            email="ivan.petrov@example.com",
            password_hash="hashed",
            first_name="Ivan",
            last_name="Petrov",
            middle_name="Sergeevich",
            phone="+79000000001",
            is_valid=True,
        ),
    )
    deleted_user = await repository.create(
        User(
            email="ghost@example.com",
            password_hash="hashed",
            first_name="Ghost",
            last_name="User",
            middle_name="",
            phone="",
            is_valid=True,
        ),
    )
    deleted_user.deleted_at = datetime.now(UTC)
    await db_session.commit()

    assert await repository.get_by_id(active_user.id) is not None
    assert await repository.get_by_email(active_user.email) is not None
    assert await repository.get_by_id(deleted_user.id) is None

    search_result = await repository.search(search="petrov")

    assert [item.id for item in search_result] == [active_user.id]


@pytest.mark.asyncio
async def test_federation_repository_loads_members_and_companies(db_session) -> None:
    graph = await seed_graph(db_session)
    repository = FederationRepository(db_session)

    loaded = await repository.get(graph.federation.id)
    listed = await repository.list_for_user(graph.owner.id)

    assert loaded is not None
    assert loaded.members[0].user.email == graph.owner.email
    assert loaded.companies[0].id == graph.company.id
    assert [item.id for item in listed] == [graph.federation.id]


@pytest.mark.asyncio
async def test_company_repository_returns_related_entities(db_session) -> None:
    graph = await seed_graph(db_session)
    repository = CompanyRepository(db_session)

    loaded = await repository.get(graph.company.id)
    companies = await repository.list_by_federation(graph.federation.id)
    tags = await repository.list_tags(graph.company.id)
    fields = await repository.list_fields(graph.company.id)
    member = await repository.get_member(graph.company.id, graph.owner.id)

    assert loaded is not None
    assert loaded.members[0].user.id == graph.owner.id
    assert loaded.projects[0].id == graph.project.id
    assert [item.id for item in companies] == [graph.company.id]
    assert [item.id for item in tags] == [graph.tag.id]
    assert [item.id for item in fields] == [graph.company_field.id]
    assert member is not None


@pytest.mark.asyncio
async def test_project_repository_loads_members_fields_and_statuses(db_session) -> None:
    graph = await seed_graph(db_session)
    repository = ProjectRepository(db_session)

    loaded = await repository.get(graph.project.id)
    projects = await repository.list_by_company(graph.company.id)
    field_link = await repository.get_field_link(
        graph.project.id, graph.company_field.id
    )
    member = await repository.get_member(graph.project.id, graph.owner.id)

    assert loaded is not None
    assert loaded.members[0].user.id == graph.owner.id
    assert loaded.field_links[0].company_field.id == graph.company_field.id
    assert len(loaded.statuses) >= 1
    assert [item.id for item in projects] == [graph.project.id]
    assert field_link is not None
    assert member is not None


@pytest.mark.asyncio
async def test_task_repository_generates_sequence_and_filters_lists(db_session) -> None:
    graph = await seed_graph(db_session)
    repository = TaskRepository(db_session)

    next_value = await repository.next_sequential_id(graph.project.id)
    later_task = await repository.create(
        Task(
            sequential_id=next_value,
            federation_id=graph.federation.id,
            company_id=graph.company.id,
            project_id=graph.project.id,
            name="Second task",
            description="",
            icon="",
            created_by_id=graph.owner.id,
            responsible_by_id=graph.owner.id,
            implement_by_id=None,
            managed_by_id=None,
            watcher_ids=[],
            coworker_ids=[],
            people_ids=[str(graph.owner.id)],
            path=[],
            status=2,
            priority=1,
            activity_at=datetime.now(UTC) + timedelta(minutes=1),
        ),
    )
    later_task.deleted_at = datetime.now(UTC)
    await db_session.commit()

    active_tasks = await repository.list(project_id=graph.project.id)
    responsible_tasks = await repository.list(responsible_by_id=graph.teammate.id)

    assert next_value == 10002
    assert [item.id for item in active_tasks] == [graph.task.id]
    assert [item.id for item in responsible_tasks] == [graph.task.id]


@pytest.mark.asyncio
async def test_comment_repository_orders_comments_by_created_at(db_session) -> None:
    graph = await seed_graph(db_session)
    earlier = datetime.now(UTC)
    later = earlier + timedelta(minutes=5)

    first = await create_comment(
        db_session,
        task_id=graph.task.id,
        created_by_id=graph.owner.id,
        body="First",
        created_at=later,
    )
    second = await create_comment(
        db_session,
        task_id=graph.task.id,
        created_by_id=graph.owner.id,
        body="Second",
        created_at=earlier,
    )

    repository = CommentRepository(db_session)
    comments = await repository.list_by_task(graph.task.id)

    assert [item.id for item in comments] == [second.id, first.id]


@pytest.mark.asyncio
async def test_reminder_repository_filters_by_task_and_user(db_session) -> None:
    graph = await seed_graph(db_session)
    repository = ReminderRepository(db_session)
    earlier = datetime.now(UTC)
    later = earlier + timedelta(hours=1)

    first = await create_reminder(
        db_session,
        task_id=graph.task.id,
        created_by_id=graph.owner.id,
        assignee_id=graph.teammate.id,
        date_from=later,
        description="Later reminder",
    )
    second = await create_reminder(
        db_session,
        task_id=graph.task.id,
        created_by_id=graph.owner.id,
        assignee_id=graph.teammate.id,
        date_from=earlier,
        description="Earlier reminder",
    )

    task_reminders = await repository.list_by_task(graph.task.id)
    user_reminders = await repository.list_by_user(graph.teammate.id)

    assert [item.id for item in task_reminders] == [second.id, first.id]
    assert [item.id for item in user_reminders] == [second.id, first.id]


@pytest.mark.asyncio
async def test_catalog_repository_returns_fields_and_records(db_session) -> None:
    graph = await seed_graph(db_session)
    repository = CatalogRepository(db_session)

    record = await repository.create_record(
        CatalogRecord(
            federation_id=graph.federation.id,
            company_id=graph.company.id,
            catalog_id=graph.catalog.id,
            created_by_id=graph.owner.id,
            field_values={"source": "web"},
            entities=[],
        ),
    )

    loaded = await repository.get(graph.catalog.id)
    listed = await repository.list_by_company(graph.company.id)
    found = await repository.find_by_name(graph.company.id, graph.catalog.name)

    assert loaded is not None
    assert loaded.fields[0].id == graph.catalog_field.id
    assert loaded.records[0].id == record.id
    assert [item.id for item in listed] == [graph.catalog.id]
    assert found is not None
