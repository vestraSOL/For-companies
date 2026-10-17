from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token, verify_password
from app.domain.enums import TASK_STATUS_LABELS, CatalogName, TaskStatus
from app.services.auth import AuthService
from app.services.catalogs import CatalogService
from app.services.comments import CommentService
from app.services.companies import CompanyService
from app.services.federations import FederationService
from app.services.profile import ProfileService
from app.services.projects import ProjectService
from app.services.reminders import ReminderService
from app.services.tasks import TaskService
from tests.factories import create_user, seed_graph


@pytest.mark.asyncio
async def test_auth_service_register_login_and_reject_duplicates(
    db_session,
    test_settings,
) -> None:
    service = AuthService(db_session, test_settings)

    user = await service.register(
        email="new@example.com",
        password="super-secret",
        first_name="Ivan",
        last_name="Petrov",
        middle_name="",
        phone="+79000000000",
    )
    same_user = await service.get_user(user.id)
    logged_user, token = await service.login(
        email="new@example.com",
        password="super-secret",
    )

    assert same_user is not None
    assert verify_password("super-secret", user.password_hash) is True
    assert logged_user.id == user.id
    assert decode_access_token(token, test_settings)["sub"] == str(user.id)

    with pytest.raises(ConflictError):
        await service.register(
            email="new@example.com",
            password="another-secret",
            first_name="Ivan",
            last_name="Petrov",
            middle_name="",
            phone="",
        )

    with pytest.raises(UnauthorizedError):
        await service.login(email="new@example.com", password="wrong-password")


@pytest.mark.asyncio
async def test_profile_service_updates_preferences(db_session) -> None:
    user = await create_user(db_session, email="profile@example.com")
    service = ProfileService(db_session)

    updated = await service.update(
        user.id,
        first_name="Updated",
        color="#ffffff",
        timezone="Asia/Yekaterinburg",
    )

    assert updated.first_name == "Updated"
    assert updated.color == "#ffffff"
    assert updated.preferences["timezone"] == "Asia/Yekaterinburg"


@pytest.mark.asyncio
async def test_federation_service_creates_and_adds_members(db_session) -> None:
    owner = await create_user(db_session, email="owner-fed@example.com")
    teammate = await create_user(db_session, email="member-fed@example.com")
    service = FederationService(db_session)

    federation = await service.create(name="Federation", creator_id=owner.id)
    updated = await service.add_member(federation.id, teammate.id)

    assert federation.name == "Federation"
    assert {member.user_id for member in updated.members} == {owner.id, teammate.id}

    with pytest.raises(ConflictError):
        await service.add_member(federation.id, teammate.id)

    with pytest.raises(NotFoundError):
        await service.add_member(federation.id, uuid4())


@pytest.mark.asyncio
async def test_company_service_creates_members_tags_and_fields(db_session) -> None:
    graph = await seed_graph(db_session)
    extra_user = await create_user(db_session, email="member-company@example.com")
    service = CompanyService(db_session)

    company = await service.create(
        federation_id=graph.federation.id,
        creator_id=graph.owner.id,
        name="Beta",
    )
    updated = await service.add_member(company.id, extra_user.id)
    tag = await service.create_tag(
        company_id=company.id,
        creator_id=graph.owner.id,
        name="Priority",
        color="#ff0000",
    )
    field = await service.create_field(
        company_id=company.id,
        name="Revenue",
        hash_value="revenue",
        description="Expected revenue",
        icon="money",
        data_type=0,
        required_on_statuses=[1, 2],
        style="secondary",
    )

    assert {member.user_id for member in updated.members} == {
        graph.owner.id,
        extra_user.id,
    }
    assert tag.name == "Priority"
    assert field.hash == "revenue"
    assert await service.planned_catalog_names() == {item.value for item in CatalogName}

    with pytest.raises(ConflictError):
        await service.create_tag(
            company_id=company.id,
            creator_id=graph.owner.id,
            name="Priority",
            color="#000000",
        )


@pytest.mark.asyncio
async def test_project_service_creates_default_statuses_and_links_fields(
    db_session,
) -> None:
    graph = await seed_graph(db_session)
    extra_user = await create_user(db_session, email="member-project@example.com")
    service = ProjectService(db_session)

    project = await service.create(
        company_id=graph.company.id,
        creator_id=graph.owner.id,
        name="Refactor",
        description="Refactor the service layer",
        responsible_by_id=graph.teammate.id,
        status_sort=None,
        fields_sort=None,
    )
    with pytest.raises(ConflictError):
        await service.create(
            company_id=graph.company.id,
            creator_id=graph.owner.id,
            name="Refactor",
            description="Duplicate",
            responsible_by_id=None,
            status_sort=None,
            fields_sort=None,
        )

    project = await service.add_member(project.id, extra_user.id)
    project = await service.add_field_link(
        project.id,
        company_field_id=graph.company_field.id,
        required_on_statuses=[1],
        style="wide",
    )
    project = await service.update(
        project.id,
        description="Updated description",
        fields_sort=["budget"],
    )

    assert len(project.statuses) == len(TASK_STATUS_LABELS)
    assert {member.user_id for member in project.members} == {
        graph.owner.id,
        extra_user.id,
    }
    assert project.field_links[0].company_field_id == graph.company_field.id
    assert project.description == "Updated description"


@pytest.mark.asyncio
async def test_task_service_creates_child_updates_status_and_soft_deletes(
    db_session,
) -> None:
    graph = await seed_graph(db_session)
    service = TaskService(db_session)

    child = await service.create(
        project_id=graph.project.id,
        creator_id=graph.owner.id,
        name="Child task",
        description="Nested task",
        responsible_by_id=graph.teammate.id,
        implement_by_id=graph.owner.id,
        managed_by_id=graph.owner.id,
        parent_task_id=graph.task.id,
        tag_ids=[graph.tag.id],
        field_values={"budget": 200},
        priority=3,
        finish_to=datetime.now(UTC) + timedelta(days=1),
        icon="bolt",
        is_epic=False,
        watcher_ids=[graph.owner.id, graph.owner.id],
        coworker_ids=[graph.teammate.id],
    )
    updated = await service.update(
        child.id,
        status=int(TaskStatus.IN_PROGRESS),
        watcher_ids=[graph.owner.id],
        coworker_ids=[graph.teammate.id, graph.teammate.id],
    )
    await service.delete(child.id)
    remaining = await service.list(project_id=graph.project.id)

    assert child.path[0] == str(graph.task.id)
    assert child.path[-1] == str(child.id)
    assert child.people_ids == [str(graph.owner.id), str(graph.teammate.id)]
    assert updated.status == int(TaskStatus.IN_PROGRESS)
    assert (
        updated.stops[-1]["status_name"]
        == TASK_STATUS_LABELS[int(TaskStatus.IN_PROGRESS)]
    )
    assert [item.id for item in remaining] == [graph.task.id]


@pytest.mark.asyncio
async def test_comment_service_creates_updates_and_soft_deletes(db_session) -> None:
    graph = await seed_graph(db_session)
    service = CommentService(db_session)

    comment = await service.create(
        task_id=graph.task.id,
        created_by_id=graph.owner.id,
        body="Need уточнить требования",
        reply_to_id=None,
        mentioned_user_ids=[graph.teammate.id],
    )
    updated = await service.update(comment.id, body="Требования уточнены")
    comments_before_delete = await service.list_by_task(graph.task.id)
    await service.delete(comment.id)
    comments_after_delete = await service.list_by_task(graph.task.id)

    assert updated.body == "Требования уточнены"
    assert comments_before_delete[0].mentioned_user_ids == [str(graph.teammate.id)]
    assert comments_after_delete == []


@pytest.mark.asyncio
async def test_reminder_service_creates_updates_and_lists_for_user(db_session) -> None:
    graph = await seed_graph(db_session)
    service = ReminderService(db_session)

    reminder = await service.create(
        task_id=graph.task.id,
        created_by_id=graph.owner.id,
        assignee_id=graph.teammate.id,
        description="Позвонить клиенту",
        comment="До обеда",
        reminder_type="manual",
        status=0,
        date_from=datetime.now(UTC) + timedelta(hours=2),
        date_to=None,
    )
    updated = await service.update(
        reminder.id,
        status=1,
        comment="После обеда",
    )
    reminders = await service.list_for_user(graph.teammate.id)

    assert updated.status == 1
    assert updated.comment == "После обеда"
    assert [item.id for item in reminders] == [reminder.id]


@pytest.mark.asyncio
async def test_catalog_service_creates_fields_records_and_blocks_reserved_names(
    db_session,
) -> None:
    graph = await seed_graph(db_session)
    service = CatalogService(db_session)

    catalog = await service.create(
        company_id=graph.company.id,
        creator_id=graph.owner.id,
        name="Contacts",
        description="Contact catalog",
    )
    field = await service.create_field(
        catalog_id=catalog.id,
        name="Telegram",
        hash_value="telegram",
        data_type=2,
        data_catalog_id=None,
    )
    record = await service.create_record(
        catalog_id=catalog.id,
        creator_id=graph.owner.id,
        field_values={"telegram": "@crm"},
        entities=[{"kind": "user", "id": str(graph.owner.id)}],
    )

    assert field.hash == "telegram"
    assert record.field_values["telegram"] == "@crm"

    with pytest.raises(ConflictError):
        await service.create(
            company_id=graph.company.id,
            creator_id=graph.owner.id,
            name=CatalogName.USERS.value,
            description="Reserved",
        )
