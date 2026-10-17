from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.common import active


class UserRepository:
    """Репозиторий пользователей"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        query = active(select(User), User).where(User.id == user_id)
        return await self.session.scalar(query)

    async def get_by_email(self, email: str) -> User | None:
        query = active(select(User), User).where(User.email == email)
        return await self.session.scalar(query)

    async def search(
        self,
        *,
        search: str,
        limit: int = 20,
    ) -> list[User]:
        """Ищет пользователей по строке поиска"""

        pattern = f"%{search.lower()}%"
        query = active(select(User), User).where(
            or_(
                User.email.ilike(pattern),
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
                User.middle_name.ilike(pattern),
            ),
        )
        query = query.order_by(User.created_at.desc()).limit(limit)
        result = await self.session.scalars(query)
        return list(result)
