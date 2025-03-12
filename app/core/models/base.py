from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid


class BaseUUID(DeclarativeBase):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )


class BaseInt(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
