from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import asyncpg
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings
from app.db.base import metadata


def _to_asyncpg_dsn(url: URL) -> str:
    return url.render_as_string(hide_password=False).replace(
        "postgresql+asyncpg://",
        "postgresql://",
        1,
    )


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = os.getenv("DATABASE_URL") or Settings().database_url
    parsed_url = make_url(database_url)
    database_name = parsed_url.database
    test_name = f"{database_name}_test"
    return parsed_url.set(database=test_name).render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def test_settings(test_database_url: str) -> Settings:
    return Settings(
        app_env="test",
        debug=False,
        database_url=test_database_url,
        jwt_secret_key="test-secret-key-with-minimum-32-bytes",
        jwt_access_token_expire_minutes=30,
    )


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_database_url: str) -> AsyncIterator[AsyncEngine]:
    target_url = make_url(test_database_url)
    database_name = target_url.database or "study_python_backend_test"
    admin_url = target_url.set(database="postgres")

    connection = await asyncpg.connect(_to_asyncpg_dsn(admin_url))
    try:
        exists = await connection.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            database_name,
        )
        if not exists:
            quoted_database_name = database_name.replace('"', '""')
            await connection.execute(f'CREATE DATABASE "{quoted_database_name}"')
    finally:
        await connection.close()

    engine = create_async_engine(test_database_url, future=True)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.drop_all)
        await connection.run_sync(metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    table_names = ", ".join(
        f'"{table.name}"' for table in reversed(metadata.sorted_tables)
    )
    async with test_engine.begin() as connection:
        await connection.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"),
        )


@pytest.fixture(scope="session")
def anyio_backend() -> Iterator[str]:
    yield "asyncio"
