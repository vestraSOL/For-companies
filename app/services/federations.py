from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.federation import Federation, FederationMember
from app.repositories.federations import FederationRepository
from app.repositories.users import UserRepository


class FederationService:
    """Сервис федераций"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.federations = FederationRepository(session)
        self.users = UserRepository(session)

    async def create(self, *, name: str, creator_id: UUID) -> Federation:
        """Создаёт федерацию"""

        existing = await self.federations.find_by_name_for_creator(name, creator_id)
        if existing:
            raise ConflictError("Federation with this name already exists.")

        federation = Federation(name=name, created_by_id=creator_id)
        await self.federations.create(federation)
        await self.federations.add_member(
            FederationMember(federation_id=federation.id, user_id=creator_id),
        )
        await self.session.commit()
        return await self.get(federation.id)

    async def get(self, federation_id: UUID) -> Federation:
        federation = await self.federations.get(federation_id)
        if not federation:
            raise NotFoundError("Federation not found.")
        return federation

    async def list_for_user(self, user_id: UUID) -> list[Federation]:
        return await self.federations.list_for_user(user_id)

    async def rename(self, federation_id: UUID, name: str) -> Federation:
        federation = await self.get(federation_id)
        federation.name = name
        await self.session.commit()
        return await self.get(federation_id)

    async def add_member(self, federation_id: UUID, user_id: UUID) -> Federation:
        """Добавляет участника в федерацию"""

        federation = await self.get(federation_id)
        user = await self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        existing = await self.federations.get_member(federation_id, user_id)
        if existing:
            raise ConflictError("User is already a federation member.")
        await self.federations.add_member(
            FederationMember(federation_id=federation.id, user_id=user.id),
        )
        await self.session.commit()
        return await self.get(federation_id)
