from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_catalog_service, get_current_user
from app.models.user import User
from app.schemas.catalog import (
    CatalogCreateRequest,
    CatalogFieldCreateRequest,
    CatalogFieldResponse,
    CatalogRecordCreateRequest,
    CatalogRecordResponse,
    CatalogResponse,
)
from app.services.catalogs import CatalogService

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


@router.get("/company/{company_id}", response_model=list[CatalogResponse])
async def list_catalogs(
    company_id: UUID,
    _: User = Depends(get_current_user),
    service: CatalogService = Depends(get_catalog_service),
) -> list[CatalogResponse]:
    catalogs = await service.list_by_company(company_id)
    return [CatalogResponse.model_validate(item) for item in catalogs]


@router.post("", response_model=CatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_catalog(
    payload: CatalogCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogResponse:
    catalog = await service.create(
        company_id=payload.company_id,
        creator_id=current_user.id,
        name=payload.name,
        description=payload.description,
    )
    return CatalogResponse.model_validate(catalog)


@router.get("/{catalog_id}", response_model=CatalogResponse)
async def get_catalog(
    catalog_id: UUID,
    _: User = Depends(get_current_user),
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogResponse:
    catalog = await service.get(catalog_id)
    return CatalogResponse.model_validate(catalog)


@router.post(
    "/{catalog_id}/fields",
    response_model=CatalogFieldResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_catalog_field(
    catalog_id: UUID,
    payload: CatalogFieldCreateRequest,
    _: User = Depends(get_current_user),
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogFieldResponse:
    field = await service.create_field(
        catalog_id=catalog_id,
        name=payload.name,
        hash_value=payload.hash,
        data_type=payload.data_type,
        data_catalog_id=payload.data_catalog_id,
    )
    return CatalogFieldResponse.model_validate(field)


@router.post(
    "/{catalog_id}/records",
    response_model=CatalogRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_catalog_record(
    catalog_id: UUID,
    payload: CatalogRecordCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogRecordResponse:
    record = await service.create_record(
        catalog_id=catalog_id,
        creator_id=current_user.id,
        field_values=payload.field_values,
        entities=payload.entities,
    )
    return CatalogRecordResponse.model_validate(record)
