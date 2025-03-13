from sqlalchemy import String, ForeignKey, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column
from core.models.base import BaseUUID
import uuid
import enum
from datetime import date


class Delivery(BaseUUID):
    __tablename__ = "delivery"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id"))
    documentdate: Mapped[date] = mapped_column(Date)
    documentnumber: Mapped[str] = mapped_column(String(15))
    supplier: Mapped[str] = mapped_column(String(150))

    def __repr__(self):
        return f"id: {self.id} №{self.documentnumber} от {self.documentdate}"
