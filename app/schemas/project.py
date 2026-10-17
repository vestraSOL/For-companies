from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import TimestampedModel, UserSummary


class ProjectCreateRequest(BaseModel):
    company_id: UUID
    name: str = Field(min_length=3, max_length=100)
    description: str = ""
    responsible_by_id: UUID | None = None
    status_sort: list[int] | None = None
    fields_sort: list[str] | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = None
    responsible_by_id: UUID | None = None
    status_sort: list[int] | None = None
    fields_sort: list[str] | None = None


class ProjectMemberCreateRequest(BaseModel):
    user_id: UUID


class ProjectFieldAttachRequest(BaseModel):
    company_field_id: UUID
    required_on_statuses: list[int] = []
    style: str = ""


class ProjectMemberResponse(TimestampedModel):
    user: UserSummary


class ProjectFieldResponse(TimestampedModel):
    project_id: UUID
    company_field_id: UUID
    required_on_statuses: list[int]
    style: str
    company_field_name: str
    company_field_hash: str
    company_field_data_type: int

    @model_validator(mode="before")
    @classmethod
    def flatten_company_field(cls, value: Any) -> Any:
        if isinstance(value, dict) or value is None:
            return value

        company_field = getattr(value, "company_field", None)
        if company_field is None:
            return value

        return {
            "id": value.id,
            "created_at": value.created_at,
            "updated_at": value.updated_at,
            "project_id": value.project_id,
            "company_field_id": value.company_field_id,
            "required_on_statuses": value.required_on_statuses,
            "style": value.style,
            "company_field_name": company_field.name,
            "company_field_hash": company_field.hash,
            "company_field_data_type": company_field.data_type,
        }


class ProjectStatusResponse(TimestampedModel):
    company_id: UUID
    project_id: UUID
    number: int
    name: str
    color: str
    description: str


class ProjectResponse(TimestampedModel):
    federation_id: UUID
    company_id: UUID
    created_by_id: UUID
    responsible_by_id: UUID | None
    name: str
    description: str
    options: dict
    status_flow: dict
    status_sort: list[int]
    fields_sort: list[str]
    status_code: int
    members: list[ProjectMemberResponse]
    fields: list[ProjectFieldResponse] = Field(validation_alias="field_links")
    statuses: list[ProjectStatusResponse]
