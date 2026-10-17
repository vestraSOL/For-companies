from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

from app.core.config import Settings
from app.core.security import verify_password
from app.models.user import User
from app.scripts import create_admin as create_admin_module


async def test_ensure_admin_user_creates_new_user(monkeypatch) -> None:
    session = AsyncMock()
    created_user: User | None = None

    class FakeUserRepository:
        def __init__(self, _session) -> None:
            self.session = _session

        async def get_by_email(self, email: str) -> User | None:
            assert email == "admin@example.com"
            return None

        async def create(self, user: User) -> User:
            nonlocal created_user
            user.id = uuid4()
            created_user = user
            return user

    monkeypatch.setattr(create_admin_module, "UserRepository", FakeUserRepository)

    result = await create_admin_module.ensure_admin_user(
        session,
        email="admin@example.com",
        password="admin",
        first_name="Admin",
        last_name="User",
        middle_name="",
        phone="",
    )

    assert result.action == "created"
    assert created_user is not None
    assert result.user.email == "admin@example.com"
    assert result.user.is_active is True
    assert result.user.is_valid is True
    assert verify_password("admin", result.user.password_hash) is True
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(result.user)


async def test_ensure_admin_user_updates_existing_user(monkeypatch) -> None:
    session = AsyncMock()
    existing = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="old-hash",
        first_name="",
        last_name="",
        middle_name="",
        phone="",
        is_active=False,
        is_valid=False,
    )

    class FakeUserRepository:
        def __init__(self, _session) -> None:
            self.session = _session

        async def get_by_email(self, email: str) -> User | None:
            assert email == "admin@example.com"
            return existing

    monkeypatch.setattr(create_admin_module, "UserRepository", FakeUserRepository)

    result = await create_admin_module.ensure_admin_user(
        session,
        email="admin@example.com",
        password="new-admin",
        first_name="Admin",
        last_name="User",
        middle_name="",
        phone="",
    )

    assert result.action == "updated"
    assert result.user.id == existing.id
    assert result.user.first_name == "Admin"
    assert result.user.last_name == "User"
    assert result.user.is_active is True
    assert result.user.is_valid is True
    assert verify_password("new-admin", result.user.password_hash) is True
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(existing)


async def test_ensure_startup_admin_user_creates_only_if_missing(monkeypatch) -> None:
    created = []

    async def fake_ensure_admin_user(session, **kwargs):
        created.append(kwargs)
        return "ok"

    class FakeSessionContext:
        async def __aenter__(self):
            return AsyncMock()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSessionMaker:
        def __call__(self):
            return FakeSessionContext()

    monkeypatch.setattr(
        create_admin_module,
        "ensure_admin_user",
        fake_ensure_admin_user,
    )

    result = await create_admin_module.ensure_startup_admin_user(
        session_maker=FakeSessionMaker(),  # type: ignore
        settings=Settings(),
    )

    assert result == "ok"
    assert created[0]["email"] == "admin@example.com"
    assert created[0]["password"] == "admin"
    assert created[0]["update_existing"] is False
