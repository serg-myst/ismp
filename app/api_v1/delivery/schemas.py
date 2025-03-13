from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import date


class Delivery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    documentdate: date
    documentnumber: str = Field(max_length=15)
    supplier: str = Field(max_length=150)
