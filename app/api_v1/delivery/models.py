from sqlalchemy import String, ForeignKey, Enum, Date, Integer, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.models.base import BaseUUID
import uuid
import enum
from datetime import date, datetime


class DeliveryTypes(enum.Enum):
    TRUST = "Доверительная"
    PALLET = "Паллетами"
    BOX = "Коробами"


class DocumentStatus(enum.Enum):
    NEW = "Новый"
    INSPECT = "Проверка"
    VERIFIED = "Проверен"
    VERIFIED_ERROR = "Проверен ошибки"


class Delivery(BaseUUID):
    __tablename__ = "delivery"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id"))
    documentdate: Mapped[date] = mapped_column(Date)
    documentnumber: Mapped[str] = mapped_column(String(15))
    supplier: Mapped[str] = mapped_column(String(150))
    supplierinn: Mapped[str] = mapped_column(String(12))
    deliverytype: Mapped[DeliveryTypes] = mapped_column(Enum(DeliveryTypes))
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.NEW
    )
    createdate: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updatedate: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"id: {self.id} №{self.documentnumber} от {self.documentdate} ({self.status})"


class DeliveryItemPlan(BaseUUID):
    __tablename__ = "deliveryitemplan"

    delivery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"))
    checking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("checking.id"))
    productpack_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("productpack.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    producedate: Mapped[date] = mapped_column(Date)

    checking = relationship(
        "Checking", back_populates="delivery_items", cascade="all, delete"
    )


class DeliveryItemFact(BaseUUID):
    __tablename__ = "deliveryitemfact"

    delivery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"))
    cis: Mapped[String] = mapped_column(String(200))
    productpack_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("productpack.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    producedate: Mapped[date] = mapped_column(Date)


class DeliveryStatusHistory(BaseUUID):
    __tablename__ = "deliverystatushistory"

    status_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    delivery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery.id"))
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus))
