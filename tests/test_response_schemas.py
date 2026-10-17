from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.enums import TaskStatus
from app.models.catalog import Catalog, CatalogField, CatalogRecord
from app.models.comment import Comment
from app.models.company import Company, CompanyField, CompanyMember, Tag
from app.models.federation import Federation, FederationMember
from app.models.project import Project, ProjectField, ProjectMember, ProjectStatus
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User
from app.schemas.catalog import CatalogResponse
from app.schemas.company import CompanyResponse
from app.schemas.federation import FederationResponse
from app.schemas.project import ProjectResponse
from app.schemas.task import TaskResponse


@dataclass(slots=True)
class ResponseGraph:
    owner: User
    teammate: User
    federation: Federation
    company: Company
    company_field: CompanyField
    tag: Tag
    project: Project
    task: Task
    catalog: Catalog
    catalog_field: CatalogField
    catalog_record: CatalogRecord


def stamp(model, *, model_id: UUID | None = None):
    timestamp = datetime.now(UTC)
    model.id = model_id or uuid4()
    model.created_at = timestamp
    model.updated_at = timestamp
    return model


def build_graph() -> ResponseGraph:
    owner = stamp(
        User(
            email="owner@example.com",
            password_hash="hashed-password",
            first_name="Ivan",
            last_name="Petrov",
            middle_name="",
            phone="+79000000001",
            color="#111111",
            has_photo=False,
        ),
    )
    teammate = stamp(
        User(
            email="teammate@example.com",
            password_hash="hashed-password",
            first_name="Petr",
            last_name="Sidorov",
            middle_name="",
            phone="+79000000002",
            color="#222222",
            has_photo=True,
        ),
    )

    federation = stamp(
        Federation(
            name="Study Federation",
            created_by_id=owner.id,
        ),
    )
    federation_member = stamp(
        FederationMember(
            federation_id=federation.id,
            user_id=owner.id,
        ),
    )
    federation_member.user = owner
    federation.members = [federation_member]

    company = stamp(
        Company(
            federation_id=federation.id,
            name="Acme",
            created_by_id=owner.id,
        ),
    )
    company_member = stamp(
        CompanyMember(
            federation_id=federation.id,
            company_id=company.id,
            user_id=owner.id,
        ),
    )
    company_member.user = owner
    company.members = [company_member]

    tag = stamp(
        Tag(
            federation_id=federation.id,
            company_id=company.id,
            created_by_id=owner.id,
            name="Backend",
            color="#111111",
        ),
    )
    company.tags = [tag]

    company_field = stamp(
        CompanyField(
            company_id=company.id,
            name="Budget",
            hash="budget",
            description="Planned budget",
            icon="wallet",
            data_type=2,
            required_on_statuses=[1],
            style="primary",
        ),
    )
    company.fields = [company_field]

    project = stamp(
        Project(
            federation_id=federation.id,
            company_id=company.id,
            created_by_id=owner.id,
            responsible_by_id=teammate.id,
            name="Launch",
            description="Main project",
            options={"status_enable": True},
            status_flow={"1": [2]},
            status_sort=[int(TaskStatus.NEW), int(TaskStatus.IN_PROGRESS)],
            fields_sort=["budget"],
            status_code=1,
        ),
    )
    project_member = stamp(ProjectMember(project_id=project.id, user_id=owner.id))
    project_member.user = owner
    project.members = [project_member]

    project_field = stamp(
        ProjectField(
            project_id=project.id,
            company_field_id=company_field.id,
            required_on_statuses=[1, 2],
            style="compact",
        ),
    )
    project_field.company_field = company_field
    project.field_links = [project_field]

    project_status = stamp(
        ProjectStatus(
            company_id=company.id,
            project_id=project.id,
            number=1,
            name="Todo",
            color="#000000",
            description="Initial status",
        ),
    )
    project.statuses = [project_status]

    company.projects = [project]
    federation.companies = [company]

    comment = stamp(
        Comment(
            task_id=uuid4(),
            created_by_id=owner.id,
            reply_to_id=None,
            body="Schema validation comment",
            mentioned_user_ids=[str(teammate.id)],
            likes={},
            pin=False,
        ),
    )
    reminder = stamp(
        Reminder(
            task_id=uuid4(),
            created_by_id=owner.id,
            assignee_id=teammate.id,
            description="Reminder",
            comment="",
            type="manual",
            status=0,
            date_from=datetime.now(UTC),
        ),
    )

    task = stamp(
        Task(
            sequential_id=10001,
            federation_id=federation.id,
            company_id=company.id,
            project_id=project.id,
            parent_task_id=None,
            name="Root task",
            description="Seed task",
            icon="rocket",
            created_by_id=owner.id,
            responsible_by_id=teammate.id,
            implement_by_id=owner.id,
            managed_by_id=owner.id,
            finished_by_id=None,
            coworker_ids=[str(teammate.id)],
            watcher_ids=[str(owner.id)],
            people_ids=[str(owner.id), str(teammate.id)],
            path=[],
            is_epic=False,
            status=1,
            priority=5,
            field_values={"budget": 100},
            meta={},
            task_entities={},
            stops=[],
            activity_at=datetime.now(UTC),
            finish_to=None,
            finished_at=None,
        ),
    )
    task.tags = [tag]
    comment.task_id = task.id
    reminder.task_id = task.id
    task.comments = [comment]
    task.reminders = [reminder]

    catalog = stamp(
        Catalog(
            federation_id=federation.id,
            company_id=company.id,
            created_by_id=owner.id,
            name="Leads",
            description="Lead source catalog",
            meta={},
        ),
    )
    catalog_field = stamp(
        CatalogField(
            catalog_id=catalog.id,
            data_catalog_id=None,
            name="Source",
            hash="source",
            data_type=2,
        ),
    )
    catalog_record = stamp(
        CatalogRecord(
            federation_id=federation.id,
            company_id=company.id,
            catalog_id=catalog.id,
            created_by_id=owner.id,
            field_values={"source": "web"},
            entities=[],
        ),
    )
    catalog.fields = [catalog_field]
    catalog.records = [catalog_record]

    return ResponseGraph(
        owner=owner,
        teammate=teammate,
        federation=federation,
        company=company,
        company_field=company_field,
        tag=tag,
        project=project,
        task=task,
        catalog=catalog,
        catalog_field=catalog_field,
        catalog_record=catalog_record,
    )


def test_company_response_validates_related_projects_from_orm() -> None:
    graph = build_graph()

    response = CompanyResponse.model_validate(graph.company)

    assert response.projects[0].id == graph.project.id
    assert response.projects[0].name == graph.project.name


def test_federation_response_validates_company_refs_from_orm() -> None:
    graph = build_graph()

    response = FederationResponse.model_validate(graph.federation)

    assert response.companies[0].id == graph.company.id
    assert response.companies[0].federation_id == graph.federation.id


def test_project_response_flattens_field_links_from_orm() -> None:
    graph = build_graph()

    response = ProjectResponse.model_validate(graph.project)

    assert response.fields[0].company_field_id == graph.company_field.id
    assert response.fields[0].company_field_name == graph.company_field.name
    assert response.fields[0].company_field_hash == graph.company_field.hash
    assert response.fields[0].company_field_data_type == graph.company_field.data_type


def test_catalog_response_validates_nested_records_from_orm() -> None:
    graph = build_graph()

    response = CatalogResponse.model_validate(graph.catalog)

    assert response.fields[0].id == graph.catalog_field.id
    assert response.records[0].id == graph.catalog_record.id


def test_task_response_converts_tags_and_nested_relations_from_orm() -> None:
    graph = build_graph()

    response = TaskResponse.model_validate(graph.task)

    assert response.tags == [graph.tag.id]
    assert response.comments[0].body == "Schema validation comment"
    assert response.reminders[0].task_id == graph.task.id
