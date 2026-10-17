from __future__ import annotations

from uuid import UUID

from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from app.core.config import Settings
from app.core.security import verify_password
from app.models.user import User
from app.repositories.users import UserRepository


class AdminAuthBackend(AuthenticationBackend):
    """Session-based auth backend for SQLAdmin."""

    def __init__(
        self,
        *,
        session_maker: async_sessionmaker[AsyncSession],
        settings: Settings,
    ) -> None:
        secret_key = settings.admin_session_secret or settings.jwt_secret_key
        super().__init__(secret_key=secret_key)
        self.session_maker = session_maker
        self.allowed_emails = {
            email.strip().lower()
            for email in settings.admin_allowed_emails.split(",")
            if email.strip()
        }

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username", "")).strip().lower()
        password = str(form.get("password", ""))
        if not email or not password:
            return False

        user = await self._get_user_by_email(email)
        if user is None or not self._can_access_admin(user):
            return False
        if not verify_password(password, user.password_hash):
            return False

        request.session.update(
            {
                "admin_user_id": str(user.id),
                "admin_user_email": user.email,
            }
        )
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        raw_user_id = request.session.get("admin_user_id")
        if not raw_user_id:
            return False

        try:
            user_id = UUID(str(raw_user_id))
        except ValueError:
            request.session.clear()
            return False

        user = await self._get_user_by_id(user_id)
        if user is None or not self._can_access_admin(user):
            request.session.clear()
            return False

        request.state.admin_user = user
        return True

    async def _get_user_by_email(self, email: str) -> User | None:
        async with self.session_maker() as session:
            repository = UserRepository(session)
            return await repository.get_by_email(email)

    async def _get_user_by_id(self, user_id: UUID) -> User | None:
        async with self.session_maker() as session:
            repository = UserRepository(session)
            return await repository.get_by_id(user_id)

    def _can_access_admin(self, user: User) -> bool:
        if not user.is_active or not user.is_valid:
            return False
        if self.allowed_emails and user.email.lower() not in self.allowed_emails:
            return False
        return True
