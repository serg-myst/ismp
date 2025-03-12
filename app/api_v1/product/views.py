from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .schemas import ProductBase, ProductGroupBase, ProductPack
from core.models.db_helper import db_helper
from fastapi import Depends

router = APIRouter(tags=["Products"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_products(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_products(session=session)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: list[ProductBase],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_products(session=session, product_in=product_in)


@router.get(
    "/product-groups/",
    response_model=list[ProductGroupBase],
    status_code=status.HTTP_200_OK,
)
async def get_products(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_product_groups(session=session)


@router.post("/product-groups/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_group_in: list[ProductGroupBase],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_product_groups(
        session=session, product_group_in=product_group_in
    )


@router.post("/product-packs/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_pack_in: list[ProductPack],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_product_packs(
        session=session, product_pack_in=product_pack_in
    )
