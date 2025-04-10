from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .schemas import Delivery, DeliveryPlan, DeliveryFact
from core.models.db_helper import db_helper


router = APIRouter(tags=["Работа с приобретением товаров"])


@router.post(
    "/create/",
    response_model=Delivery,
    status_code=status.HTTP_201_CREATED,
    summary="метод создает/обновляет приобретение товаров",
)
async def create_delivery(
    delivery_in: Delivery,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_delivery(session, delivery_in=delivery_in)


@router.post(
    "/get-plan/",
    status_code=status.HTTP_201_CREATED,
    summary="метод возвращает плановую поставку в разрезе групповых упаковок (паллет) по датам производства",
)
async def get_delivery_plan(
    delivery_in: DeliveryPlan,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_delivery_plan(session=session, delivery_in=delivery_in)


@router.post(
    "/send-fact/",
    status_code=status.HTTP_201_CREATED,
    summary="метод записывает фактические данные приобретения в разрезе"
    " групповых упаковок (паллет) по датам производства",
)
async def send_delivery_fact(
    delivery_in: list[DeliveryFact],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_delivery_fact(session=session, delivery_in=delivery_in)
