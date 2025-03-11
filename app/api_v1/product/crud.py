from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from .models import Product, ProductGroup
from .schemas import Product as Product_Schemas


async def get_products(session: AsyncSession) -> list[Product]:
    stmt = select(Product).order_by(Product.name)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)


async def get_product_groups(session: AsyncSession) -> list[ProductGroup]:
    stmt = select(ProductGroup).order_by(ProductGroup.id)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)
