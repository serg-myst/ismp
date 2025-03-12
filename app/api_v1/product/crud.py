from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from .models import Product, ProductGroup, ProductPack
from .schemas import ProductGroupBase
from .schemas import ProductPack as ProductPackSchema
from .schemas import ProductBase as Product_Base
from typing import List


async def get_products(session: AsyncSession) -> list[Product]:
    stmt = select(Product).order_by(Product.name)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)


async def create_products(
    session: AsyncSession, product_in: List[Product_Base]
) -> List[Product]:

    stmt = insert(Product).values([product.dict() for product in product_in])
    stmt = stmt.on_conflict_do_update(
        index_elements=["product_id", "organization_id"],
        set_={
            "name": stmt.excluded.name,
            "fullname": stmt.excluded.fullname,
            "code": stmt.excluded.code,
            "article": stmt.excluded.article,
        },
    ).returning(Product)

    result = await session.execute(stmt)
    await session.commit()
    items = result.scalars().all()
    return list(items)


async def get_product_groups(session: AsyncSession) -> list[ProductGroup]:
    stmt = select(ProductGroup).order_by(ProductGroup.id)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)


async def create_product_groups(
    session: AsyncSession, product_group_in: List[ProductGroupBase]
) -> List[ProductGroup]:

    stmt = insert(ProductGroup).values([group.dict() for group in product_group_in])
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "name": stmt.excluded.name,
            "description": stmt.excluded.description,
        },
    ).returning(ProductGroup)

    result = await session.execute(stmt)
    await session.commit()
    items = result.scalars().all()
    return list(items)


async def create_product_packs(
    session: AsyncSession, product_pack_in: List[ProductPackSchema]
) -> List[ProductPack]:

    stmt = insert(ProductPack).values([pack.dict() for pack in product_pack_in])
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "name": stmt.excluded.name,
            "numerator": stmt.excluded.numerator,
            "denominator": stmt.excluded.denominator,
        },
    ).returning(ProductPack)

    result = await session.execute(stmt)
    await session.commit()
    items = result.scalars().all()
    return list(items)
