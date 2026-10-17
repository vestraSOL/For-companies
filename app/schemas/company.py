from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import EntityRef, TimestampedModel, UserSummary


class CompanyCreateRequest(BaseModel):
    federation_id: UUID
    name: str = Field(min_length=3, max_length=100)


class CompanyUpdateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)


class CompanyMemberCreateRequest(BaseModel):
    user_id: UUID


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(default="#000000", max_length=20)


class TagUpdateRequest(TagCreateRequest):
    pass


class CompanyFieldCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    hash: str = Field(min_length=3, max_length=50, pattern=r"^[a-z_]+$")
    description: str = ""
    icon: str = ""
    data_type: int
    required_on_statuses: list[int] = []
    style: str = ""


class TagResponse(TimestampedModel):
    federation_id: UUID
    company_id: UUID
    name: str
    color: str
    created_by_id: UUID


class CompanyFieldResponse(TimestampedModel):
    company_id: UUID
    name: str
    hash: str
    description: str
    icon: str
    data_type: int
    required_on_statuses: list[int]
    style: str


class CompanyMemberResponse(TimestampedModel):
    federation_id: UUID
    company_id: UUID
    user: UserSummary


class ProjectShortResponse(EntityRef):
    pass


class CompanyResponse(TimestampedModel):
    federation_id: UUID
    name: str
    members: list[CompanyMemberResponse]
    tags: list[TagResponse]
    fields: list[CompanyFieldResponse]
    projects: list[ProjectShortResponse]
