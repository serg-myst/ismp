from sqlalchemy import String, ForeignKey, Enum, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column
from core.models.base import BaseUUID
import uuid
import enum
from datetime import date


class DeliveryTypes(enum.Enum):
    TRUST = "Доверительная"
    PALLET = "Паллетами"
    BOX = "Коробами"


class Delivery(BaseUUID):
    __tablename__ = "delivery"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id"))
    documentdate: Mapped[date] = mapped_column(Date)
    documentnumber: Mapped[str] = mapped_column(String(15))
    supplier: Mapped[str] = mapped_column(String(150))
    supplierinn: Mapped[str] = mapped_column(String(12))
    deliverytype: Mapped[DeliveryTypes] = mapped_column(Enum(DeliveryTypes))

    def __repr__(self):
        return f"id: {self.id} №{self.documentnumber} от {self.documentdate}"


class DeliveryItemPlan(BaseUUID):
    __tablename__ = "deliveryitemplan"

    delivery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"))
    checking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("checking.id"))
    productpack_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("productpack.id"))
    quantity: Mapped[int] = mapped_column(Integer)
