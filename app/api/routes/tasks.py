from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_task_service
from app.models.user import User
from app.schemas.task import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from app.services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    project_id: UUID | None = Query(default=None),
    company_id: UUID | None = Query(default=None),
    status_filter: int | None = Query(default=None, alias="status"),
    responsible_by_id: UUID | None = Query(default=None),
    _: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    tasks = await service.list(
        project_id=project_id,
        company_id=company_id,
        status=status_filter,
        responsible_by_id=responsible_by_id,
    )
    return [TaskResponse.model_validate(task) for task in tasks]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await service.create(
        project_id=payload.project_id,
        creator_id=current_user.id,
        name=payload.name,
        description=payload.description,
        responsible_by_id=payload.responsible_by_id,
        implement_by_id=payload.implement_by_id,
        managed_by_id=payload.managed_by_id,
        parent_task_id=payload.parent_task_id,
        tag_ids=payload.tag_ids,
        field_values=payload.field_values,
        priority=payload.priority,
        finish_to=payload.finish_to,
        icon=payload.icon,
        is_epic=payload.is_epic,
        watcher_ids=payload.watcher_ids,
        coworker_ids=payload.coworker_ids,
    )
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    _: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await service.get(task_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    payload: TaskUpdateRequest,
    _: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    task = await service.update(task_id, **payload.model_dump(exclude_none=True))
    return TaskResponse.model_validate(task)
