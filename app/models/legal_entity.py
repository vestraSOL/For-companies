from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
if TYPE_CHECKING:
    from app.models import Company
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin,Base


class LegalEntity(UUIDPrimaryKeyMixin,TimestampMixin,Base):
    __tablename__="legal_entities"
    name: Mapped[str]=mapped_column(String(100))
    company_id: Mapped[UUID]=mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    company: Mapped["Company"]=relationship(back_populates="")
    def __str__(self)->str:
        return f"LegalEntity(name={self.name},company_id={self.company_id})"
