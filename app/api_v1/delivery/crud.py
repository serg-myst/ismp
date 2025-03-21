from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete
from .schemas import Delivery as DeliverySchemas, DeliveryPlan
from .models import Delivery, DeliveryItemPlan, DeliveryTypes
from api_v1.cischecking.models import Checking
from api_v1.product.models import ProductPack, Product


async def create_delivery(
    session: AsyncSession,
    delivery_in: DeliverySchemas,
) -> Delivery:
    stmt = insert(Delivery).values(**delivery_in.model_dump())

    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "documentdate": stmt.excluded.documentdate,
            "documentnumber": stmt.excluded.documentnumber,
            "supplier": stmt.excluded.supplier,
            "supplierinn": stmt.excluded.supplierinn,
        },
    ).returning(Delivery)

    result = await session.execute(stmt)
    await session.commit()
    item = result.scalars().first()

    return item


async def create_plan(delivery_id, pack_type, session: AsyncSession):

    stmt = (
        select(
            Checking.id,
            Checking.delivery_id,
            Checking.product_id,
            Checking.productpack_id,
            Checking.quantity_upd,
        )
        .where(Checking.delivery_id == delivery_id)
        .where(
            Checking.packagetype == "LEVEL2"
            if pack_type == DeliveryTypes.PALLET
            else "LEVEL1"
        )
    )

    result = await session.execute(stmt)
    items = result.fetchall()

    data_to_insert = [
        {
            "checking_id": item.id,
            "delivery_id": item.delivery_id,
            "product_id": item.product_id,
            "productpack_id": item.productpack_id,
            "quantity": item.quantity_upd,
        }
        for item in items
    ]

    if not data_to_insert:
        return []

    insert_stmt = (
        insert(DeliveryItemPlan)
        .values(data_to_insert)
        .returning(
            DeliveryItemPlan.id,
            DeliveryItemPlan.delivery_id,
            DeliveryItemPlan.product_id,
            DeliveryItemPlan.productpack_id,
            DeliveryItemPlan.quantity,
        )
    )
    await session.execute(insert_stmt)
    await session.commit()

    select_stmt = (
        select(
            DeliveryItemPlan.id,
            DeliveryItemPlan.delivery_id,
            DeliveryItemPlan.product_id,
            Product.product_id.label("product_id_1c"),
            Product.name.label("product_name"),
            DeliveryItemPlan.productpack_id,
            ProductPack.name.label("pack_name"),
            ProductPack.numerator,
            ProductPack.denominator,
            Checking.cis,
            DeliveryItemPlan.quantity,
        )
        .where(DeliveryItemPlan.delivery_id == delivery_id)
        .join(Checking, DeliveryItemPlan.checking_id == Checking.id)
        .join(ProductPack, DeliveryItemPlan.productpack_id == ProductPack.id)
        .join(Product, DeliveryItemPlan.product_id == Product.id)
    )

    final_result = await session.execute(select_stmt)
    return final_result.mappings().all()


async def create_delivery_plan(session: AsyncSession, delivery_in: DeliveryPlan):

    stmt = select(Delivery.deliverytype).where(Delivery.id == delivery_in.delivery_id)

    result = await session.execute(stmt)
    pack_type = result.scalars().first()

    if not pack_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Поставка с id = {delivery_in.delivery_id} не найдена",
        )

    stmt = delete(DeliveryItemPlan).where(
        DeliveryItemPlan.delivery_id == delivery_in.delivery_id
    )
    await session.execute(stmt)
    await session.commit()

    result = await create_plan(delivery_in.delivery_id, pack_type, session)

    return result
