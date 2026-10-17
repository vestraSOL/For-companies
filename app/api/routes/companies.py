from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_company_service, get_current_user
from app.models.user import User
from app.schemas.company import (
    CompanyCreateRequest,
    CompanyFieldCreateRequest,
    CompanyFieldResponse,
    CompanyMemberCreateRequest,
    CompanyResponse,
    CompanyUpdateRequest,
    TagCreateRequest,
    TagResponse,
    TagUpdateRequest,
)
from app.services.companies import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyResponse])
async def list_companies(
    federation_id: UUID,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> list[CompanyResponse]:
    companies = await service.list_by_federation(federation_id)
    return [CompanyResponse.model_validate(item) for item in companies]


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    company = await service.create(
        federation_id=payload.federation_id,
        creator_id=current_user.id,
        name=payload.name,
    )
    return CompanyResponse.model_validate(company)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    company = await service.get(company_id)
    return CompanyResponse.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def rename_company(
    company_id: UUID,
    payload: CompanyUpdateRequest,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    company = await service.rename(company_id, payload.name)
    return CompanyResponse.model_validate(company)


@router.post("/{company_id}/members", response_model=CompanyResponse)
async def add_company_member(
    company_id: UUID,
    payload: CompanyMemberCreateRequest,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    company = await service.add_member(company_id, payload.user_id)
    return CompanyResponse.model_validate(company)


@router.get("/{company_id}/tags", response_model=list[TagResponse])
async def list_tags(
    company_id: UUID,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> list[TagResponse]:
    tags = await service.list_tags(company_id)
    return [TagResponse.model_validate(tag) for tag in tags]


@router.post(
    "/{company_id}/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    company_id: UUID,
    payload: TagCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> TagResponse:
    tag = await service.create_tag(
        company_id=company_id,
        creator_id=current_user.id,
        name=payload.name,
        color=payload.color,
    )
    return TagResponse.model_validate(tag)


@router.patch("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    payload: TagUpdateRequest,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> TagResponse:
    tag = await service.update_tag(tag_id, name=payload.name, color=payload.color)
    return TagResponse.model_validate(tag)


@router.get("/{company_id}/fields", response_model=list[CompanyFieldResponse])
async def list_company_fields(
    company_id: UUID,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> list[CompanyFieldResponse]:
    fields = await service.list_fields(company_id)
    return [CompanyFieldResponse.model_validate(field) for field in fields]


@router.post(
    "/{company_id}/fields",
    response_model=CompanyFieldResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company_field(
    company_id: UUID,
    payload: CompanyFieldCreateRequest,
    _: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyFieldResponse:
    field = await service.create_field(
        company_id=company_id,
        name=payload.name,
        hash_value=payload.hash,
        description=payload.description,
        icon=payload.icon,
        data_type=payload.data_type,
        required_on_statuses=payload.required_on_statuses,
        style=payload.style,
    )
    return CompanyFieldResponse.model_validate(field)
