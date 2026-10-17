from __future__ import annotations

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.admin import setup_admin
from app.core.security import get_password_hash
from app.models.company import Company
from app.models.federation import Federation
from app.models.user import User


async def login_to_admin(
    client: AsyncClient,
    *,
    email: str,
    password: str,
) -> None:
    response = await client.post(
        "/admin/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 302
    assert response.headers["location"].endswith("/admin/")


async def test_sqladmin_login_and_index_access(test_engine, test_settings) -> None:
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        session.add(
            User(
                email="admin@example.com",
                password_hash=get_password_hash("super-secret"),
                first_name="Admin",
                last_name="User",
                middle_name="",
                phone="",
                is_active=True,
                is_valid=True,
            )
        )
        await session.commit()

    app = FastAPI()
    setup_admin(
        app,
        session_maker=session_factory,
        admin_engine=test_engine,
        settings=test_settings,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        response = await client.get("/admin/")
        assert response.status_code == 302
        assert response.headers["location"].endswith("/admin/login")

        await login_to_admin(
            client,
            email="admin@example.com",
            password="super-secret",
        )

        response = await client.get("/admin/")
        assert response.status_code == 200
        assert "Study CRM Admin" in response.text

        response = await client.get("/admin/user/list")
        assert response.status_code == 200
        assert "admin@example.com" in response.text


async def test_sqladmin_company_create_page_and_post_work(
    test_engine,
    test_settings,
) -> None:
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        owner = User(
            email="owner@example.com",
            password_hash=get_password_hash("super-secret"),
            first_name="Owner",
            last_name="User",
            middle_name="",
            phone="",
            is_active=True,
            is_valid=True,
        )
        session.add(owner)
        await session.flush()

        federation = Federation(
            name="Test Federation",
            created_by_id=owner.id,
        )
        session.add(federation)
        await session.commit()

    app = FastAPI()
    setup_admin(
        app,
        session_maker=session_factory,
        admin_engine=test_engine,
        settings=test_settings,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        await login_to_admin(
            client,
            email="owner@example.com",
            password="super-secret",
        )

        response = await client.get("/admin/company/create")
        assert response.status_code == 200
        assert 'name="federation"' in response.text
        assert 'name="created_by_id"' not in response.text

        response = await client.post(
            "/admin/company/create",
            data={
                "federation": str(federation.id),
                "name": "Created via admin",
                "sms_options": '{"enabled": true}',
                "save": "Save",
            },
        )
        assert response.status_code == 302
        assert response.headers["location"].endswith("/admin/company/list")

    async with session_factory() as session:
        created_company = await session.scalar(
            select(Company).where(Company.name == "Created via admin")
        )
        assert created_company is not None
        assert created_company.created_by_id == owner.id


async def test_sqladmin_respects_allowed_email_list(test_engine, test_settings) -> None:
    restricted_settings = test_settings.model_copy(
        update={"admin_allowed_emails": "allowed@example.com"}
    )
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        session.add(
            User(
                email="blocked@example.com",
                password_hash=get_password_hash("super-secret"),
                first_name="Blocked",
                last_name="User",
                middle_name="",
                phone="",
                is_active=True,
                is_valid=True,
            )
        )
        await session.commit()

    app = FastAPI()
    setup_admin(
        app,
        session_maker=session_factory,
        admin_engine=test_engine,
        settings=restricted_settings,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        response = await client.post(
            "/admin/login",
            data={"username": "blocked@example.com", "password": "super-secret"},
        )
        assert response.status_code == 400
        assert "Invalid credentials." in response.text
