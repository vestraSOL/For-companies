from __future__ import annotations

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.admin.auth import AdminAuthBackend
from app.admin.views import ADMIN_VIEWS
from app.core.config import Settings, get_settings
from app.db.session import SessionLocal, engine


def setup_admin(
    app: FastAPI,
    *,
    session_maker: async_sessionmaker[AsyncSession] = SessionLocal,
    admin_engine: AsyncEngine = engine,
    settings: Settings | None = None,
) -> Admin:
    current_settings = settings or get_settings()
    authentication_backend = AdminAuthBackend(
        session_maker=session_maker,
        settings=current_settings,
    )
    admin = Admin(
        app,
        engine=admin_engine,
        session_maker=session_maker,
        base_url=current_settings.admin_base_url,
        title=current_settings.admin_title,
        debug=current_settings.debug,
        authentication_backend=authentication_backend,
    )
    for view in ADMIN_VIEWS:
        admin.add_view(view)
    return admin
