from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from core.models.base import BaseUUID
from sqlalchemy.orm import relationship


class Organization(BaseUUID):
    __tablename__ = "organization"

    name: Mapped[str] = mapped_column(String(50))
    fullname: Mapped[str] = mapped_column(String(250))
    inn: Mapped[str] = mapped_column(String(12))
    kpp: Mapped[str] = mapped_column(String(9))

    def __repr__(self):
        return f"{self.name}. инн {self.inn}"
