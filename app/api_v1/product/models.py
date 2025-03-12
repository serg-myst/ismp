from sqlalchemy import String, ForeignKey, UUID, UniqueConstraint, Integer
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


class ProductPack(BaseUUID):
    __tablename__ = "productpack"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50))
    numerator: Mapped[int] = mapped_column(Integer)
    denominator: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return f"{self.name} ({self.numerator/self.denominator})"


class Product(BaseUUID):
    __tablename__ = "product"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id"))
    name: Mapped[str] = mapped_column(String(100))
    fullname: Mapped[str] = mapped_column(String(1024))
    product_group_id: Mapped[int] = mapped_column(ForeignKey(ProductGroup.id))
    code: Mapped[str] = mapped_column(String(11))
    article: Mapped[str] = mapped_column(String(50))

    pg = relationship(ProductGroup, backref="product", uselist=True, lazy="selectin")
    pack = relationship(ProductPack, backref="pack", uselist=True, lazy="selectin")

    __table_args__ = (UniqueConstraint("organization_id", "product_id"),)

    def __repr__(self):
        return f"id: {self.product_id}, name: ({self.code}) {self.name}"
