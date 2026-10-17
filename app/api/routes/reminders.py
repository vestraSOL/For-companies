from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_reminder_service
from app.models.user import User
from app.schemas.reminder import (
    ReminderCreateRequest,
    ReminderResponse,
    ReminderStatusUpdateRequest,
    ReminderUpdateRequest,
)
from app.services.reminders import ReminderService

router = APIRouter(tags=["reminders"])


@router.get("/reminders", response_model=list[ReminderResponse])
async def list_my_reminders(
    current_user: User = Depends(get_current_user),
    service: ReminderService = Depends(get_reminder_service),
) -> list[ReminderResponse]:
    reminders = await service.list_for_user(current_user.id)
    return [ReminderResponse.model_validate(reminder) for reminder in reminders]


@router.get("/tasks/{task_id}/reminders", response_model=list[ReminderResponse])
async def list_task_reminders(
    task_id: UUID,
    _: User = Depends(get_current_user),
    service: ReminderService = Depends(get_reminder_service),
) -> list[ReminderResponse]:
    reminders = await service.list_by_task(task_id)
    return [ReminderResponse.model_validate(reminder) for reminder in reminders]


@router.post(
    "/tasks/{task_id}/reminders",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reminder(
    task_id: UUID,
    payload: ReminderCreateRequest,
    current_user: User = Depends(get_current_user),
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderResponse:
    reminder = await service.create(
        task_id=task_id,
        created_by_id=current_user.id,
        assignee_id=payload.assignee_id,
        description=payload.description,
        comment=payload.comment,
        reminder_type=payload.type,
        status=payload.status,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )
    return ReminderResponse.model_validate(reminder)


@router.patch("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    payload: ReminderUpdateRequest,
    _: User = Depends(get_current_user),
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderResponse:
    reminder = await service.update(
        reminder_id, **payload.model_dump(exclude_none=True)
    )
    return ReminderResponse.model_validate(reminder)


@router.patch("/reminders/{reminder_id}/status", response_model=ReminderResponse)
async def update_reminder_status(
    reminder_id: UUID,
    payload: ReminderStatusUpdateRequest,
    _: User = Depends(get_current_user),
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderResponse:
    reminder = await service.update(reminder_id, status=payload.status)
    return ReminderResponse.model_validate(reminder)
