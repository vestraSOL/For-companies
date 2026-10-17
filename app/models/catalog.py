from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Catalog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "catalogs"
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_company_catalog_name"),
    )

    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(5000), default="")
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)

    company: Mapped["Company"] = relationship(back_populates="catalogs")
    created_by: Mapped["User"] = relationship()
    fields: Mapped[list["CatalogField"]] = relationship(
        back_populates="catalog",
        foreign_keys="CatalogField.catalog_id",
        cascade="all, delete-orphan",
    )
    records: Mapped[list["CatalogRecord"]] = relationship(
        back_populates="catalog",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return self.name


class CatalogField(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "catalog_fields"
    __table_args__ = (
        UniqueConstraint("catalog_id", "hash", name="uq_catalog_field_hash"),
    )

    catalog_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogs.id", ondelete="CASCADE")
    )
    data_catalog_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("catalogs.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(String(100))
    hash: Mapped[str] = mapped_column(String(50))
    data_type: Mapped[int]

    catalog: Mapped["Catalog"] = relationship(
        back_populates="fields",
        foreign_keys=[catalog_id],
    )
    data_catalog: Mapped["Catalog | None"] = relationship(
        foreign_keys=[data_catalog_id],
    )

    def __str__(self) -> str:
        return self.name


class CatalogRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "catalog_records"

    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    catalog_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogs.id", ondelete="CASCADE")
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    field_values: Mapped[dict] = mapped_column(JSONB, default=dict)
    entities: Mapped[list[dict]] = mapped_column(JSONB, default=list)

    catalog: Mapped["Catalog"] = relationship(back_populates="records")
    created_by: Mapped["User"] = relationship()


if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User
