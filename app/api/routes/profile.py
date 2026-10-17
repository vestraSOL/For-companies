from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_profile_service
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services.profile import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    user = await service.get(current_user.id)
    return ProfileResponse.model_validate(user)


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    user = await service.update(
        current_user.id, **payload.model_dump(exclude_none=True)
    )
    return ProfileResponse.model_validate(user)
