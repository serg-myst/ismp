from sqlalchemy import String, Integer, ForeignKey, UUID, UniqueConstraint, Column
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from core.models.base import BaseUUID, BaseInt
import uuid


class ProductGroup(BaseInt):
    __tablename__ = "productgroup"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class Product(BaseUUID):
    __tablename__ = "product"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id"))
    name: Mapped[str] = mapped_column(String(100))
    fullname: Mapped[str] = mapped_column(String(1024))
    product_group_id: Mapped[int] = mapped_column(ForeignKey(ProductGroup.id))

    pg = relationship(ProductGroup, backref="product", uselist=True, lazy="selectin")

    __table_args__ = (UniqueConstraint("organization_id", "product_id"),)

    def __repr__(self):
        return f"id: {self.product_id}, name: {self.name}"
