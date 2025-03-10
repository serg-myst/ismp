from pydantic import BaseModel, Field, ConfigDict
import uuid


class OrganizationUpdate(BaseModel):
    __tablename__ = "organization"

    name: str | None = None
    fullname: str | None = None
    inn: str | None = None
    kpp: str | None = None


class Organization(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str = Field(max_length=50)
    fullname: str = Field(max_length=250)
    inn: str = Field(max_length=12)
    kpp: str = Field(max_length=9)
