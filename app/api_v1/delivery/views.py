from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .schemas import Delivery
from core.models.db_helper import db_helper


router = APIRouter(tags=["Deliveries"])


@router.post("/", response_model=Delivery, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    delivery_in: Delivery,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_delivery(session, delivery_in=delivery_in)
