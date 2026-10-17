from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.federation import Federation, FederationMember
from app.repositories.common import active


class FederationRepository:
    """Репозиторий федераций"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, federation: Federation) -> Federation:
        self.session.add(federation)
        await self.session.flush()
        await self.session.refresh(federation)
        return federation

    async def get(self, federation_id: UUID) -> Federation | None:
        query = (
            active(select(Federation), Federation)
            .where(Federation.id == federation_id)
            .execution_options(populate_existing=True)
            .options(
                selectinload(Federation.members).selectinload(FederationMember.user),
                selectinload(Federation.companies),
            )
        )
        return await self.session.scalar(query)

    async def list_for_user(self, user_id: UUID) -> list[Federation]:
        """Возвращает федерации пользователя"""

        query = (
            active(select(Federation), Federation)
            .join(FederationMember, FederationMember.federation_id == Federation.id)
            .where(
                FederationMember.user_id == user_id,
                FederationMember.deleted_at.is_(None),
            )
            .execution_options(populate_existing=True)
            .options(
                selectinload(Federation.members).selectinload(FederationMember.user),
                selectinload(Federation.companies),
            )
            .order_by(Federation.created_at.desc())
        )
        result = await self.session.scalars(query)
        return list(result.unique())

    async def find_by_name_for_creator(
        self, name: str, created_by_id: UUID
    ) -> Federation | None:
        query = active(select(Federation), Federation).where(
            Federation.name == name,
            Federation.created_by_id == created_by_id,
        )
        return await self.session.scalar(query)

    async def add_member(self, member: FederationMember) -> FederationMember:
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def get_member(
        self, federation_id: UUID, user_id: UUID
    ) -> FederationMember | None:
        query = active(select(FederationMember), FederationMember).where(
            FederationMember.federation_id == federation_id,
            FederationMember.user_id == user_id,
        )
        return await self.session.scalar(query)
