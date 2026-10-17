from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.users import UserRepository


class ProfileService:
    """Сервис профиля пользователя"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def get(self, user_id: UUID) -> User:
        user = await self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    async def update(
        self,
        user_id: UUID,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        phone: str | None = None,
        color: str | None = None,
        timezone: str | None = None,
    ) -> User:
        """Обновляет профиль пользователя"""

        user = await self.get(user_id)
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if middle_name is not None:
            user.middle_name = middle_name
        if phone is not None:
            user.phone = phone
        if color is not None:
            user.color = color
        if timezone is not None:
            user.preferences = {**user.preferences, "timezone": timezone}

        await self.session.commit()
        await self.session.refresh(user)
        return user
