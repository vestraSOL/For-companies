from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Catalog, CatalogField, CatalogRecord
from app.repositories.common import active


class CatalogRepository:
    """Репозиторий каталогов"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, catalog: Catalog) -> Catalog:
        self.session.add(catalog)
        await self.session.flush()
        await self.session.refresh(catalog)
        return catalog

    async def get(self, catalog_id: UUID) -> Catalog | None:
        query = (
            active(select(Catalog), Catalog)
            .where(Catalog.id == catalog_id)
            .options(selectinload(Catalog.fields), selectinload(Catalog.records))
        )
        return await self.session.scalar(query)

    async def list_by_company(self, company_id: UUID) -> list[Catalog]:
        """Возвращает каталоги компании"""

        query = (
            active(select(Catalog), Catalog)
            .where(Catalog.company_id == company_id)
            .options(selectinload(Catalog.fields))
            .order_by(Catalog.created_at.desc())
        )
        result = await self.session.scalars(query)
        return list(result.unique())

    async def find_by_name(self, company_id: UUID, name: str) -> Catalog | None:
        query = active(select(Catalog), Catalog).where(
            Catalog.company_id == company_id, Catalog.name == name
        )
        return await self.session.scalar(query)

    async def create_field(self, field: CatalogField) -> CatalogField:
        self.session.add(field)
        await self.session.flush()
        await self.session.refresh(field)
        return field

    async def create_record(self, record: CatalogRecord) -> CatalogRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record
