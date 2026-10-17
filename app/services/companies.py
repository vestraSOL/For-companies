from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.enums import RESERVED_CATALOG_NAMES
from app.models.company import Company, CompanyField, CompanyMember, Tag
from app.repositories.companies import CompanyRepository
from app.repositories.federations import FederationRepository
from app.repositories.users import UserRepository


class CompanyService:
    """Сервис компаний"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.companies = CompanyRepository(session)
        self.federations = FederationRepository(session)
        self.users = UserRepository(session)

    async def create(
        self, *, federation_id: UUID, creator_id: UUID, name: str
    ) -> Company:
        """Создаёт компанию"""

        federation = await self.federations.get(federation_id)
        if not federation:
            raise NotFoundError("Federation not found.")
        existing = await self.companies.find_by_name(federation_id, name)
        if existing:
            raise ConflictError("Company with this name already exists.")

        company = Company(
            federation_id=federation_id,
            created_by_id=creator_id,
            name=name,
        )
        await self.companies.create(company)
        await self.companies.add_member(
            CompanyMember(
                federation_id=federation_id,
                company_id=company.id,
                user_id=creator_id,
            ),
        )
        await self.session.commit()
        return await self.get(company.id)

    async def get(self, company_id: UUID) -> Company:
        company = await self.companies.get(company_id)
        if not company:
            raise NotFoundError("Company not found.")
        return company

    async def list_by_federation(self, federation_id: UUID) -> list[Company]:
        return await self.companies.list_by_federation(federation_id)

    async def rename(self, company_id: UUID, name: str) -> Company:
        company = await self.get(company_id)
        company.name = name
        await self.session.commit()
        return await self.get(company_id)

    async def add_member(self, company_id: UUID, user_id: UUID) -> Company:
        company = await self.get(company_id)
        user = await self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        existing = await self.companies.get_member(company_id, user_id)
        if existing:
            raise ConflictError("User is already a company member.")
        await self.companies.add_member(
            CompanyMember(
                federation_id=company.federation_id,
                company_id=company_id,
                user_id=user_id,
            ),
        )
        await self.session.commit()
        return await self.get(company_id)

    async def create_tag(
        self,
        *,
        company_id: UUID,
        creator_id: UUID,
        name: str,
        color: str,
    ) -> Tag:
        """Создаёт тег компании"""

        company = await self.get(company_id)
        existing = await self.companies.find_tag_by_name(company_id, name)
        if existing:
            raise ConflictError("Tag with this name already exists.")
        tag = Tag(
            federation_id=company.federation_id,
            company_id=company_id,
            created_by_id=creator_id,
            name=name,
            color=color,
        )
        await self.companies.create_tag(tag)
        await self.session.commit()
        return tag

    async def list_tags(self, company_id: UUID) -> list[Tag]:
        await self.get(company_id)
        return await self.companies.list_tags(company_id)

    async def update_tag(self, tag_id: UUID, *, name: str, color: str) -> Tag:
        tag = await self.companies.get_tag(tag_id)
        if not tag:
            raise NotFoundError("Tag not found.")
        tag.name = name
        tag.color = color
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def create_field(
        self,
        *,
        company_id: UUID,
        name: str,
        hash_value: str,
        description: str,
        icon: str,
        data_type: int,
        required_on_statuses: list[int],
        style: str,
    ) -> CompanyField:
        """Создаёт поле компании"""

        await self.get(company_id)
        existing = await self.companies.list_fields(company_id)
        if any(item.hash == hash_value for item in existing):
            raise ConflictError("Company field hash already exists.")
        field = CompanyField(
            company_id=company_id,
            name=name,
            hash=hash_value,
            description=description,
            icon=icon,
            data_type=data_type,
            required_on_statuses=required_on_statuses,
            style=style,
        )
        await self.companies.create_field(field)
        await self.session.commit()
        return field

    async def list_fields(self, company_id: UUID) -> list[CompanyField]:
        await self.get(company_id)
        return await self.companies.list_fields(company_id)

    async def planned_catalog_names(self) -> set[str]:
        return RESERVED_CATALOG_NAMES
