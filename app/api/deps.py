from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.user import User
from app.services.auth import AuthService
from app.services.catalogs import CatalogService
from app.services.comments import CommentService
from app.services.companies import CompanyService
from app.services.federations import FederationService
from app.services.profile import ProfileService
from app.services.projects import ProjectService
from app.services.reminders import ReminderService
from app.services.tasks import TaskService

bearer_scheme = HTTPBearer(auto_error=False)


def get_app_settings() -> Settings:
    return get_settings()


def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_app_settings),
) -> AuthService:
    return AuthService(session, settings)


def get_profile_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProfileService:
    return ProfileService(session)


def get_federation_service(
    session: AsyncSession = Depends(get_db_session),
) -> FederationService:
    return FederationService(session)


def get_company_service(
    session: AsyncSession = Depends(get_db_session),
) -> CompanyService:
    return CompanyService(session)


def get_project_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProjectService:
    return ProjectService(session)


def get_task_service(
    session: AsyncSession = Depends(get_db_session),
) -> TaskService:
    return TaskService(session)


def get_comment_service(
    session: AsyncSession = Depends(get_db_session),
) -> CommentService:
    return CommentService(session)


def get_reminder_service(
    session: AsyncSession = Depends(get_db_session),
) -> ReminderService:
    return ReminderService(session)


def get_catalog_service(
    session: AsyncSession = Depends(get_db_session),
) -> CatalogService:
    return CatalogService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_app_settings),
) -> User:
    """Возвращает пользователя по bearer-токену"""

    if credentials is None:
        raise UnauthorizedError("Authentication credentials are required.")

    payload = decode_access_token(credentials.credentials, settings)
    user_id = UUID(payload["sub"])
    user = await auth_service.get_user(user_id)
    if not user:
        raise UnauthorizedError("User not found for the provided token.")
    return user
