from sqlalchemy import Column, String
from core.models.base import Base


class Organization(Base):
    __tablename__ = "organization"

    name = Column(String(50))
    fullname = Column(String(250))
    inn = Column(String(12))
    kpp = Column(String(9))

    def __repr__(self):
        return f"{self.name}. инн {self.inn}"
