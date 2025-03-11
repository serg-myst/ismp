from pydantic import BaseModel, ConfigDict, Field
import uuid


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


class Product(ProductBase):
    id: uuid.UUID
