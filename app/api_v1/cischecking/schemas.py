from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import date, datetime
from .models import CisStatus, PackType
from typing import Optional, List


class Checking(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parent_id: uuid.UUID
    delivery_id: uuid.UUID
    product_id: uuid.UUID
    productpack_id: uuid.UUID
    cis: str = Field(max_length=100)
    status: CisStatus
    produceddate: date
    gtin: str = Field(max_length=25)
    ownerinn: str = Field(max_length=12)
    ownername: str = Field(max_length=150)
    packagetype: PackType
    quantity: int
    quantity_upd: int
    checked: bool


empty_uuid = uuid.UUID(int=0)


class CheckingCreate(BaseModel):
    delivery_id: uuid.UUID
    product_id: uuid.UUID
    cis: str = Field(max_length=100)
    productpack_id: uuid.UUID
    quantity_upd: int


class CisResponse(BaseModel):
    id: Optional[uuid.UUID] = Field(default=None, exclude=False)
    parent_id: Optional[uuid.UUID] = Field(default=None, exclude=False)
    delivery_id: Optional[uuid.UUID] = Field(default=None, exclude=False)
    product_id: Optional[uuid.UUID] = Field(default=None, exclude=False)
    productpack_id: Optional[uuid.UUID] = Field(default=None, exclude=False)
    quantity: Optional[int] = Field(default=None, exclude=False)
    quantity_upd: Optional[int] = Field(default=None, exclude=False)
    ownererror: bool = Field(default=None, exclude=False)
    statuserror: bool = Field(default=None, exclude=False)
    checked: bool = Field(default=None, exclude=False)
    monopallet: bool = Field(default=None, exclude=False)
    quantityerror: bool = Field(default=None, exclude=False)
    expirationdateerror: bool = Field(default=None, exclude=False)

    cis: str
    status: str
    gtin: str
    ownerinn: str = Field(..., alias="ownerInn")
    ownername: str = Field(..., alias="ownerName")
    packagetype: str = Field(..., alias="packageType")
    produceddate: Optional[datetime] = Field(None, alias="producedDate")
    expirationdate: Optional[datetime] = Field(None, alias="expirationDate")
    child: List[str]

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        }


class CisUnit(BaseModel):
    delivery_id: uuid.UUID
    cis: str
