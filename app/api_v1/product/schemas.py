from pydantic import BaseModel, ConfigDict, Field
import uuid
from .models import TimeType


class ProductGroupBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(max_length=255)
    description: str = Field(max_length=255)


class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    organization_id: uuid.UUID
    name: str = Field(max_length=100)
    fullname: str = Field(max_length=1024)
    product_group_id: int
    code: str = Field(max_length=11)
    article: str = Field(max_length=50)
    bestbeforedate: int
    shelflifeunit: TimeType


class Product(ProductBase):
    id: uuid.UUID


class ProductPack(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    name: str = Field(max_length=50)
    numerator: int
    denominator: int
