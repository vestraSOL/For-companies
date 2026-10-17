from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import EntityRef, TimestampedModel, UserSummary


class FederationCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class FederationMemberCreateRequest(BaseModel):
    user_id: UUID


class FederationMemberResponse(TimestampedModel):
    user: UserSummary


class CompanyShortResponse(EntityRef):
    federation_id: UUID


class FederationResponse(TimestampedModel):
    name: str
    members: list[FederationMemberResponse]
    companies: list[CompanyShortResponse]
