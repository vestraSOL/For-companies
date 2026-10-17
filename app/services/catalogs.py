from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.enums import RESERVED_CATALOG_NAMES
from app.models.catalog import Catalog, CatalogField, CatalogRecord
from app.repositories.catalogs import CatalogRepository
from app.repositories.companies import CompanyRepository


class CatalogService:
    """Сервис каталогов"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.catalogs = CatalogRepository(session)
        self.companies = CompanyRepository(session)

    async def create(
        self,
        *,
        company_id: UUID,
        creator_id: UUID,
        name: str,
        description: str,
    ) -> Catalog:
        """Создаёт каталог"""

        company = await self.companies.get(company_id)
        if not company:
            raise NotFoundError("Company not found.")
        if name in RESERVED_CATALOG_NAMES:
            raise ConflictError("Catalog name is reserved for study exercises.")
        existing = await self.catalogs.find_by_name(company_id, name)
        if existing:
            raise ConflictError("Catalog with this name already exists.")
        catalog = Catalog(
            federation_id=company.federation_id,
            company_id=company_id,
            created_by_id=creator_id,
            name=name,
            description=description,
        )
        await self.catalogs.create(catalog)
        await self.session.commit()
        return await self.get(catalog.id)

    async def get(self, catalog_id: UUID) -> Catalog:
        catalog = await self.catalogs.get(catalog_id)
        if not catalog:
            raise NotFoundError("Catalog not found.")
        return catalog

    async def list_by_company(self, company_id: UUID) -> list[Catalog]:
        return await self.catalogs.list_by_company(company_id)

    async def create_field(
        self,
        *,
        catalog_id: UUID,
        name: str,
        hash_value: str,
        data_type: int,
        data_catalog_id: UUID | None,
    ) -> CatalogField:
        """Создаёт поле каталога"""

        catalog = await self.get(catalog_id)
        if any(field.hash == hash_value for field in catalog.fields):
            raise ConflictError("Catalog field hash already exists.")
        field = CatalogField(
            catalog_id=catalog_id,
            name=name,
            hash=hash_value,
            data_type=data_type,
            data_catalog_id=data_catalog_id,
        )
        await self.catalogs.create_field(field)
        await self.session.commit()
        return field

    async def create_record(
        self,
        *,
        catalog_id: UUID,
        creator_id: UUID,
        field_values: dict,
        entities: list[dict],
    ) -> CatalogRecord:
        """Создаёт запись каталога"""

        catalog = await self.get(catalog_id)
        record = CatalogRecord(
            federation_id=catalog.federation_id,
            company_id=catalog.company_id,
            catalog_id=catalog_id,
            created_by_id=creator_id,
            field_values=field_values,
            entities=entities,
        )
        await self.catalogs.create_record(record)
        await self.session.commit()
        return record
