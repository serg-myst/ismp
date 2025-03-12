from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import date
from .models import CisStatus, PackType


class Checking(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parent_id: uuid.UUID
    delivery_id: uuid.UUID
    product_id: uuid.UUID
    cis: str = Field(max_length=100)
    status: CisStatus
    produceddate: date
    gtin: str = Field(max_length=25)
    ownerinn: str = Field(max_length=12)
    ownername: str = Field(max_length=150)
    packagetype: PackType
    quantity: int
    checked: bool
