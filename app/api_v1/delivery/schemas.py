from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import date, datetime
from typing import Optional
from .models import DeliveryTypes


class Delivery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    documentdate: date
    documentnumber: str = Field(max_length=15)
    supplier: str = Field(max_length=150)
    supplierinn: str = Field(max_length=12)
    deliverytype: DeliveryTypes


class DeliveryPlan(BaseModel):
    delivery_id: uuid.UUID


class DeliveryPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    delivery_id: uuid.UUID
    product_id: uuid.UUID
    checking_id: uuid.UUID
    productpack_id: uuid.UUID
    cis: str = Field(default=None, exclude=False)
    quantity: int


class DeliveryFact(BaseModel):
    delivery_id: uuid.UUID
    product_id: uuid.UUID
    cis: str = Field(default=None, exclude=False)
    productpack_id: uuid.UUID
    quantity: int
