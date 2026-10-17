from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedModel


class CatalogCreateRequest(BaseModel):
    company_id: UUID
    name: str = Field(min_length=3, max_length=100)
    description: str = ""


class CatalogFieldCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    hash: str = Field(min_length=3, max_length=50, pattern=r"^[a-z_]+$")
    data_type: int
    data_catalog_id: UUID | None = None


class CatalogRecordCreateRequest(BaseModel):
    field_values: dict = {}
    entities: list[dict] = []


class CatalogFieldResponse(TimestampedModel):
    catalog_id: UUID
    data_catalog_id: UUID | None
    name: str
    hash: str
    data_type: int


class CatalogRecordResponse(TimestampedModel):
    federation_id: UUID
    company_id: UUID
    catalog_id: UUID
    created_by_id: UUID
    field_values: dict
    entities: list[dict]


class CatalogResponse(TimestampedModel):
    federation_id: UUID
    company_id: UUID
    created_by_id: UUID
    name: str
    description: str
    meta: dict
    fields: list[CatalogFieldResponse]
    records: list[CatalogRecordResponse]
