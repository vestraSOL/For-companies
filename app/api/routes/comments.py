from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_comment_service, get_current_user
from app.models.user import User
from app.schemas.comment import (
    CommentCreateRequest,
    CommentResponse,
    CommentUpdateRequest,
)
from app.schemas.common import MessageResponse
from app.services.comments import CommentService

router = APIRouter(tags=["comments"])


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def list_task_comments(
    task_id: UUID,
    _: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
) -> list[CommentResponse]:
    comments = await service.list_by_task(task_id)
    return [CommentResponse.model_validate(comment) for comment in comments]


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    task_id: UUID,
    payload: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
) -> CommentResponse:
    comment = await service.create(
        task_id=task_id,
        created_by_id=current_user.id,
        body=payload.body,
        reply_to_id=payload.reply_to_id,
        mentioned_user_ids=payload.mentioned_user_ids,
    )
    return CommentResponse.model_validate(comment)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    payload: CommentUpdateRequest,
    _: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
) -> CommentResponse:
    comment = await service.update(comment_id, body=payload.body)
    return CommentResponse.model_validate(comment)


@router.delete("/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: UUID,
    _: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
) -> MessageResponse:
    await service.delete(comment_id)
    return MessageResponse(message="Comment deleted.")
