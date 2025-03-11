from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .schemas import Product, ProductGroupBase
from core.models.db_helper import db_helper
from fastapi import Depends

router = APIRouter(tags=["Products"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_products(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_products(session=session)


@router.get(
    "/pg/", response_model=list[ProductGroupBase], status_code=status.HTTP_200_OK
)
async def get_products(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_product_groups(session=session)
