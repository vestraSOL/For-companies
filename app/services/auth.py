from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.users import UserRepository


class AuthService:
    """Сервис аутентификации"""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)

    async def register(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        middle_name: str,
        phone: str,
    ) -> User:
        """Регистрирует пользователя"""

        existing_user = await self.users.get_by_email(email)
        if existing_user:
            raise ConflictError("User with this email already exists.")

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone=phone,
            is_valid=True,
            valid_at=datetime.now(UTC),
        )
        await self.users.create(user)
        await self.session.commit()
        return user

    async def login(self, *, email: str, password: str) -> tuple[User, str]:
        """Выполняет вход пользователя"""

        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")

        token = create_access_token(subject=str(user.id), settings=self.settings)
        return user, token

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.users.get_by_id(user_id)
