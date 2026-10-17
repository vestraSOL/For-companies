from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.users import UserRepository

DEFAULT_ADMIN_FIRST_NAME = "Admin"
DEFAULT_ADMIN_LAST_NAME = "User"
DEFAULT_ADMIN_MIDDLE_NAME = ""
DEFAULT_ADMIN_PHONE = ""


@dataclass(slots=True)
class CreateAdminResult:
    action: str
    user: User


async def ensure_admin_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    middle_name: str,
    phone: str,
    update_existing: bool = True,
) -> CreateAdminResult:
    repository = UserRepository(session)
    user = await repository.get_by_email(email)

    if user is None:
        password_hash = get_password_hash(password)
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone=phone,
            is_active=True,
            is_valid=True,
            valid_at=datetime.now(UTC),
        )
        await repository.create(user)
        await session.commit()
        await session.refresh(user)
        return CreateAdminResult(action="created", user=user)

    if not update_existing:
        return CreateAdminResult(action="exists", user=user)

    password_hash = get_password_hash(password)
    user.password_hash = password_hash
    user.is_active = True
    user.is_valid = True
    user.valid_at = datetime.now(UTC)
    if not user.first_name:
        user.first_name = first_name
    if not user.last_name:
        user.last_name = last_name
    if not user.middle_name:
        user.middle_name = middle_name
    if not user.phone:
        user.phone = phone

    await session.commit()
    await session.refresh(user)
    return CreateAdminResult(action="updated", user=user)


async def ensure_startup_admin_user(
    *,
    session_maker: async_sessionmaker[AsyncSession],
    settings: Settings,
) -> CreateAdminResult | None:
    email = settings.bootstrap_admin_email.strip().lower()
    password = settings.bootstrap_admin_password
    if not email:
        raise ValueError("BOOTSTRAP_ADMIN_EMAIL must not be empty.")
    if not password:
        raise ValueError("BOOTSTRAP_ADMIN_PASSWORD must not be empty.")

    async with session_maker() as session:
        return await ensure_admin_user(
            session,
            email=email,
            password=password,
            first_name=DEFAULT_ADMIN_FIRST_NAME,
            last_name=DEFAULT_ADMIN_LAST_NAME,
            middle_name=DEFAULT_ADMIN_MIDDLE_NAME,
            phone=DEFAULT_ADMIN_PHONE,
            update_existing=False,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update an admin-capable user for the study CRM project.",
    )
    parser.add_argument("--email", default="admin@example.com")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--first-name", default="Admin")
    parser.add_argument("--last-name", default="User")
    parser.add_argument("--middle-name", default="")
    parser.add_argument("--phone", default="")
    return parser.parse_args()


async def _async_main() -> int:
    get_settings()
    args = parse_args()
    async with SessionLocal() as session:
        result = await ensure_admin_user(
            session,
            email=args.email.strip().lower(),
            password=args.password,
            first_name=args.first_name,
            last_name=args.last_name,
            middle_name=args.middle_name,
            phone=args.phone,
        )

    print(
        f"Admin user {result.action}: "
        f"email={result.user.email} password={args.password}",
    )
    return 0


def main() -> int:
    return asyncio.run(_async_main())


if __name__ == "__main__":
    raise SystemExit(main())
