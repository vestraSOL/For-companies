from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Federation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "federations"

    name: Mapped[str] = mapped_column(String(100))
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_by: Mapped["User"] = relationship()
    members: Mapped[list["FederationMember"]] = relationship(
        back_populates="federation",
        cascade="all, delete-orphan",
    )
    companies: Mapped[list["Company"]] = relationship(back_populates="federation")

    def __str__(self) -> str:
        return self.name


class FederationMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "federation_members"
    __table_args__ = (
        UniqueConstraint(
            "federation_id",
            "user_id",
            name="uq_federation_member_user",
        ),
    )

    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    federation: Mapped["Federation"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User
