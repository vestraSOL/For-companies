from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    federation_id: Mapped[UUID] = mapped_column(
        ForeignKey("federations.id", ondelete="CASCADE")
    )
    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    responsible_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(5000), default="")
    options: Mapped[dict] = mapped_column(JSONB, default=dict)
    status_flow: Mapped[dict] = mapped_column(JSONB, default=dict)
    status_sort: Mapped[list[int]] = mapped_column(JSONB, default=list)
    fields_sort: Mapped[list[str]] = mapped_column(JSONB, default=list)
    status_code: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)

    company: Mapped["Company"] = relationship(back_populates="projects")
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    responsible_by: Mapped["User | None"] = relationship(
        foreign_keys=[responsible_by_id]
    )
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    field_links: Mapped[list["ProjectField"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    statuses: Mapped[list["ProjectStatus"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")

    def __str__(self) -> str:
        return self.name


class ProjectMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member_user"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class ProjectField(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_fields"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "company_field_id",
            name="uq_project_company_field",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    company_field_id: Mapped[UUID] = mapped_column(
        ForeignKey("company_fields.id", ondelete="CASCADE")
    )
    required_on_statuses: Mapped[list[int]] = mapped_column(JSONB, default=list)
    style: Mapped[str] = mapped_column(String(20), default="")

    project: Mapped["Project"] = relationship(back_populates="field_links")
    company_field: Mapped["CompanyField"] = relationship(back_populates="projects")


class ProjectStatus(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_statuses"
    __table_args__ = (
        UniqueConstraint("project_id", "number", name="uq_project_status_number"),
    )

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    color: Mapped[str] = mapped_column(String(30), default="#000000")
    description: Mapped[str] = mapped_column(String(5000), default="")

    project: Mapped["Project"] = relationship(back_populates="statuses")

    def __str__(self) -> str:
        return f"{self.number}: {self.name}"


if TYPE_CHECKING:
    from app.models.company import Company, CompanyField
    from app.models.task import Task
    from app.models.user import User
