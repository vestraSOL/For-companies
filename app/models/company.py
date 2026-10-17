from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100))
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    sms_options: Mapped[dict] = mapped_column(JSONB, default=dict)

    federation: Mapped["Federation"] = relationship(back_populates="companies")
    created_by: Mapped["User"] = relationship()
    members: Mapped[list["CompanyMember"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list["Tag"]] = relationship(back_populates="company")
    fields: Mapped[list["CompanyField"]] = relationship(back_populates="company")
    projects: Mapped[list["Project"]] = relationship(back_populates="company")
    catalogs: Mapped[list["Catalog"]] = relationship(back_populates="company")

    def __str__(self) -> str:
        return self.name


class CompanyMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "company_members"
    __table_args__ = (
        UniqueConstraint("company_id", "user_id", name="uq_company_member_user"),
    )

    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    company: Mapped["Company"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class Tag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_company_tag_name"),
    )

    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(20), default="#000000")
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    company: Mapped["Company"] = relationship(back_populates="tags")
    created_by: Mapped["User"] = relationship()

    def __str__(self) -> str:
        return self.name


class CompanyField(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "company_fields"
    __table_args__ = (
        UniqueConstraint("company_id", "hash", name="uq_company_field_hash"),
    )

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100))
    hash: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(5000), default="")
    icon: Mapped[str] = mapped_column(String(50), default="")
    data_type: Mapped[int]
    required_on_statuses: Mapped[list[int]] = mapped_column(JSONB, default=list)
    style: Mapped[str] = mapped_column(String(20), default="")

    company: Mapped["Company"] = relationship(back_populates="fields")
    projects: Mapped[list["ProjectField"]] = relationship(
        back_populates="company_field"
    )

    def __str__(self) -> str:
        return (
            f"{self.company.name}: {self.name}"
            if hasattr(self, "company")
            else self.name
        )


if TYPE_CHECKING:
    from app.models.catalog import Catalog
    from app.models.federation import Federation
    from app.models.project import Project, ProjectField
    from app.models.user import User
