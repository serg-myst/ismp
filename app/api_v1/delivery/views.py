import uuid

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


@router.post(
    "/get-differences/",
    summary="метод возвращает расхождения плана и факта по приобретению",
)
async def get_delivery_differences_plan_fact(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_delivery_differences(session=session, delivery_id=delivery_id)


@router.post(
    "/get-fact/",
    summary="метод возвращает фактические данные приобретения. используем для создания документа в сторонней базе",
)
async def get_delivery_differences_plan_fact(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_delivery_fact(session=session, delivery_id=delivery_id)


@router.post(
    "/get-delivery-status/",
    status_code=status.HTTP_200_OK,
    summary="метод возвращает текущий статус документа приобретения",
)
async def get_delivery_status(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_delivery_status(session=session, delivery_id=delivery_id)


@router.post(
    "/get-delivery-status-history/",
    status_code=status.HTTP_200_OK,
    summary="метод возвращает историю статусов документа приобретения",
)
async def get_delivery_status(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_delivery_status_history(
        session=session, delivery_id=delivery_id
    )
