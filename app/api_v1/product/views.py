from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .schemas import ProductBase, ProductGroupBase, ProductPack
from core.models.db_helper import db_helper
from fastapi import Depends

router = APIRouter(tags=["Работа с номенклатурой"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="метод возвращает список товаров вместе с реквизитами, товарными группами, единицами измерения",
)
async def get_products(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_products(session=session)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="метод создает/обновляет номенклатуру",
)
async def create_product(
    product_in: list[ProductBase],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_products(session=session, product_in=product_in)


@router.get(
    "/product-groups/",
    response_model=list[ProductGroupBase],
    status_code=status.HTTP_200_OK,
    summary="метод возвращает товарные группы системы честный знак",
)
async def get_products(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_product_groups(session=session)


@router.post(
    "/product-groups/",
    status_code=status.HTTP_201_CREATED,
    summary="метод создает/обновляет товарные группы",
)
async def create_product_groups(
    product_group_in: list[ProductGroupBase],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_product_groups(
        session=session, product_group_in=product_group_in
    )


@router.post(
    "/product-packs/",
    status_code=status.HTTP_201_CREATED,
    summary="метод создает/обновляет товарные упаковки",
)
async def create_product_packs(
    product_pack_in: list[ProductPack],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_product_packs(
        session=session, product_pack_in=product_pack_in
    )
