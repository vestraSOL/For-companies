from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company, CompanyField, CompanyMember, Tag
from app.repositories.common import active


class CompanyRepository:
    """Репозиторий компаний"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, company: Company) -> Company:
        self.session.add(company)
        await self.session.flush()
        await self.session.refresh(company)
        return company

    async def get(self, company_id: UUID) -> Company | None:
        """Возвращает компанию по идентификатору"""

        query = (
            active(select(Company), Company)
            .where(Company.id == company_id)
            .execution_options(populate_existing=True)
            .options(
                selectinload(Company.members).selectinload(CompanyMember.user),
                selectinload(Company.tags),
                selectinload(Company.fields),
                selectinload(Company.projects),
                selectinload(Company.catalogs),
            )
        )
        return await self.session.scalar(query)

    async def list_by_federation(self, federation_id: UUID) -> list[Company]:
        query = (
            active(select(Company), Company)
            .where(Company.federation_id == federation_id)
            .execution_options(populate_existing=True)
            .options(
                selectinload(Company.members).selectinload(CompanyMember.user),
                selectinload(Company.tags),
                selectinload(Company.fields),
                selectinload(Company.projects),
            )
            .order_by(Company.created_at.desc())
        )
        result = await self.session.scalars(query)
        return list(result.unique())

    async def find_by_name(self, federation_id: UUID, name: str) -> Company | None:
        query = active(select(Company), Company).where(
            Company.federation_id == federation_id,
            Company.name == name,
        )
        return await self.session.scalar(query)

    async def add_member(self, member: CompanyMember) -> CompanyMember:
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def get_member(self, company_id: UUID, user_id: UUID) -> CompanyMember | None:
        query = active(select(CompanyMember), CompanyMember).where(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == user_id,
        )
        return await self.session.scalar(query)

    async def create_tag(self, tag: Tag) -> Tag:
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def list_tags(self, company_id: UUID) -> list[Tag]:
        query = (
            active(select(Tag), Tag)
            .where(Tag.company_id == company_id)
            .order_by(Tag.created_at.desc())
        )
        result = await self.session.scalars(query)
        return list(result)

    async def get_tag(self, tag_id: UUID) -> Tag | None:
        query = active(select(Tag), Tag).where(Tag.id == tag_id)
        return await self.session.scalar(query)

    async def find_tag_by_name(self, company_id: UUID, name: str) -> Tag | None:
        query = active(select(Tag), Tag).where(
            Tag.company_id == company_id, Tag.name == name
        )
        return await self.session.scalar(query)

    async def create_field(self, field: CompanyField) -> CompanyField:
        self.session.add(field)
        await self.session.flush()
        await self.session.refresh(field)
        return field

    async def list_fields(self, company_id: UUID) -> list[CompanyField]:
        query = (
            active(select(CompanyField), CompanyField)
            .where(
                CompanyField.company_id == company_id,
            )
            .order_by(CompanyField.created_at.asc())
        )
        result = await self.session.scalars(query)
        return list(result)

    async def get_field(self, field_id: UUID) -> CompanyField | None:
        query = active(select(CompanyField), CompanyField).where(
            CompanyField.id == field_id
        )
        return await self.session.scalar(query)
