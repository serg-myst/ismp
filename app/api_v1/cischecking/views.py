import uuid

from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.db_helper import db_helper
from fastapi import Depends
from . import crud
from .models import PackType
from .schemas import CheckingCreate, CisUnit

router = APIRouter(tags=["Работа по проверке кодов маркировки"])


@router.post(
    "/check/",
    status_code=status.HTTP_201_CREATED,
    summary="метод принимает коды групповых упаковок из приобретения "
    "товаров и отправляет на проверку в систему честный знак",
)
async def create_check_list(
    cis_in: list[CheckingCreate],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_check_cis(session=session, cis_in=cis_in)


@router.get(
    "/get-hierarchy-plan/{delivery_id}/{use_unit}",
    status_code=status.HTTP_200_OK,
    summary="метод возвращает иерархический список проверенных кодов маркировки приобретения товаров",
)
async def get_hierarchy(
    delivery_id: uuid.UUID,
    use_unit: bool,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_hierarchy(
        session=session, delivery_id=delivery_id, use_unit=use_unit
    )


@router.get(
    "/get-product-by-package-plan/{delivery_id}/{package}",
    status_code=status.HTTP_200_OK,
    summary="методв возвращает проверенные коды маркировки приобретения товаров по переданной упаковке",
)
async def get_product_by_package(
    delivery_id: uuid.UUID,
    package: PackType,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_product_by_package(
        session=session, delivery_id=delivery_id, package=package
    )


@router.post(
    "/get-units-by-cis/",
    status_code=status.HTTP_200_OK,
    summary="метод возвращает данные переданного кода маркировки",
)
async def get_units_by_cis(
    cis_in: CisUnit,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_units_by_cis(session=session, cis_in=cis_in)


@router.get(
    "/get-cis-with-errors/{delivery_id}",
    status_code=status.HTTP_200_OK,
    summary="Метод позволяет получить иерархический список кодов маркировки с ошибками",
)
async def get_cis_with_errors(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_cis_with_errors(session=session, delivery_id=delivery_id)
