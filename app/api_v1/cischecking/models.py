from sqlalchemy import String, ForeignKey, BigInteger, Enum, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from core.models.base import BaseUUID
import uuid
import enum
from typing import List
from datetime import date


class PackType(enum.Enum):
    UNIT = "UNIT"
    GROUP = "GROUP"
    SET = "SET"
    BUNDLE = "BUNDLE"
    BOX = "BOX"
    ATK = "ATK"
    LEVEL1 = "LEVEL1"
    LEVEL2 = "LEVEL2"
    LEVEL3 = "LEVEL3"
    LEVEL4 = "LEVEL4"


class CisStatus(enum.Enum):
    EMITTED = "EMITTED"
    APPLIED = "APPLIED"
    INTRODUCED = "INTRODUCED"
    WRITTEN_OFF = "WRITTEN_OFF"
    RETIRED = "RETIRED"
    WITHDRAWN = "WITHDRAWN"
    DISAGGREGATION = "DISAGGREGATION"
    DISAGGREGATED = "DISAGGREGATED"
    APPLIED_NOT_PAID = "APPLIED_NOT_PAID"


class Checking(BaseUUID):
    __tablename__ = "checking"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.UUID(int=0)
    )
    delivery_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"))
    productpack_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("productpack.id"))
    cis: Mapped[str] = mapped_column(String(100))
    status: Mapped[CisStatus] = mapped_column(Enum(CisStatus))
    produceddate: Mapped[date] = mapped_column(Date)
    expirationdate: Mapped[date] = mapped_column(Date)
    gtin: Mapped[str] = mapped_column(String(25))
    ownerinn: Mapped[str] = mapped_column(String(12))
    ownername: Mapped[str] = mapped_column(String(150))
    packagetype: Mapped[PackType] = mapped_column(Enum(PackType))
    quantity: Mapped[int] = mapped_column(BigInteger)
    quantity_upd: Mapped[int] = mapped_column(BigInteger)
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    ownererror: Mapped[bool] = mapped_column(Boolean, default=False)
    statuserror: Mapped[bool] = mapped_column(Boolean, default=False)
    quantityerror: Mapped[bool] = mapped_column(Boolean, default=False)
    expirationdateerror: Mapped[bool] = mapped_column(Boolean, default=False)
    monopallet: Mapped[bool] = mapped_column(Boolean, default=False)

    delivery_items: Mapped[List["DeliveryItemPlan"]] = relationship(
        "DeliveryItemPlan",
        back_populates="checking",
        cascade="all, delete",
    )
