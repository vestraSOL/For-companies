from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_federation_service
from app.models.user import User
from app.schemas.federation import (
    FederationCreateRequest,
    FederationMemberCreateRequest,
    FederationResponse,
)
from app.services.federations import FederationService

router = APIRouter(prefix="/federations", tags=["federations"])


@router.get("", response_model=list[FederationResponse])
async def list_federations(
    current_user: User = Depends(get_current_user),
    service: FederationService = Depends(get_federation_service),
) -> list[FederationResponse]:
    federations = await service.list_for_user(current_user.id)
    return [FederationResponse.model_validate(item) for item in federations]


@router.post("", response_model=FederationResponse, status_code=status.HTTP_201_CREATED)
async def create_federation(
    payload: FederationCreateRequest,
    current_user: User = Depends(get_current_user),
    service: FederationService = Depends(get_federation_service),
) -> FederationResponse:
    federation = await service.create(name=payload.name, creator_id=current_user.id)
    return FederationResponse.model_validate(federation)


@router.get("/{federation_id}", response_model=FederationResponse)
async def get_federation(
    federation_id: UUID,
    _: User = Depends(get_current_user),
    service: FederationService = Depends(get_federation_service),
) -> FederationResponse:
    federation = await service.get(federation_id)
    return FederationResponse.model_validate(federation)


@router.patch("/{federation_id}", response_model=FederationResponse)
async def rename_federation(
    federation_id: UUID,
    payload: FederationCreateRequest,
    _: User = Depends(get_current_user),
    service: FederationService = Depends(get_federation_service),
) -> FederationResponse:
    federation = await service.rename(federation_id, payload.name)
    return FederationResponse.model_validate(federation)


@router.post("/{federation_id}/members", response_model=FederationResponse)
async def add_federation_member(
    federation_id: UUID,
    payload: FederationMemberCreateRequest,
    _: User = Depends(get_current_user),
    service: FederationService = Depends(get_federation_service),
) -> FederationResponse:
    federation = await service.add_member(federation_id, payload.user_id)
    return FederationResponse.model_validate(federation)
