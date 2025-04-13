from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete, func
from sqlalchemy import insert as usual_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from datetime import datetime
import uuid
from collections import defaultdict
import asyncio
from .models import (
    Delivery,
    DeliveryItemPlan,
    DeliveryItemFact,
    DeliveryStatusHistory,
    DocumentStatus,
    DeliveryItemPlanFact,
)
from api_v1.cischecking.models import Checking
from api_v1.product.models import ProductPack, Product
from .schemas import Delivery as DeliverySchemas, DeliveryPlan, DeliveryFact
from .service import update_delivery_plan_fact


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

    stmt = insert(DeliveryStatusHistory).values(
        {
            "delivery_id": delivery_in.id,
            "status": DocumentStatus.NEW,
            "status_date": datetime.now(),
        }
    )
    await session.execute(stmt)
    await session.commit()

    return item


async def create_plan(delivery_id, session: AsyncSession):

    empty_uuid = uuid.UUID(int=0)

    Parent = aliased(Checking)
    Child = aliased(Checking)

    stmt = (
        select(
            Child.delivery_id,
            Child.product_id,
            Child.parent_id.label("checking_id"),
            Parent.productpack_id,
            Child.produceddate,
            func.sum(Child.quantity).label("quantity"),
        )
        .join(Parent, Child.parent_id == Parent.id)
        .where(Parent.parent_id == empty_uuid, Parent.delivery_id == delivery_id)
        .group_by(
            Child.delivery_id,
            Child.product_id,
            Child.parent_id,
            Parent.productpack_id,
            Child.produceddate,
        )
    )

    result = await session.execute(stmt)
    items = result.fetchall()

    data_to_insert = [
        {
            "checking_id": item.checking_id,
            "delivery_id": item.delivery_id,
            "product_id": item.product_id,
            "productpack_id": item.productpack_id,
            "producedate": item.produceddate,
            "quantity": item.quantity,
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
            DeliveryItemPlan.producedate,
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
            DeliveryItemPlan.producedate,
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
    rows = final_result.fetchall()

    grouped_data = defaultdict(
        lambda: {
            "id": None,
            "delivery_id": None,
            "product_id": None,
            "product_id_1c": None,
            "product_name": None,
            "productpack_id": None,
            "pack_name": None,
            "numerator": None,
            "denominator": None,
            "cis": None,
            "producedate": [],
        }
    )

    for row in rows:
        key = (
            row.delivery_id,
            row.product_id,
            row.cis,
            row.productpack_id,
        )

        grouped_data[key]["id"] = row.id
        grouped_data[key]["delivery_id"] = row.delivery_id
        grouped_data[key]["product_id"] = row.product_id
        grouped_data[key]["product_id_1c"] = row.product_id_1c
        grouped_data[key]["product_name"] = row.product_name
        grouped_data[key]["productpack_id"] = row.productpack_id
        grouped_data[key]["pack_name"] = row.pack_name
        grouped_data[key]["numerator"] = row.numerator
        grouped_data[key]["denominator"] = row.denominator
        grouped_data[key]["cis"] = row.cis

        grouped_data[key]["producedate"].append(
            {"date": row.producedate, "quantity": row.quantity}
        )

    result = list(grouped_data.values())

    return result


async def create_delivery_plan(session: AsyncSession, delivery_in: DeliveryPlan):

    stmt = select(Delivery.deliverytype).where(Delivery.id == delivery_in.delivery_id)

    result = await session.execute(stmt)
    find_delivery = result.scalar_one_or_none()

    if find_delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"приобретение с id = {delivery_in.delivery_id} не найдено в базе",
        )

    stmt = delete(DeliveryItemPlan).where(
        DeliveryItemPlan.delivery_id == delivery_in.delivery_id
    )
    await session.execute(stmt)
    await session.commit()

    result = await create_plan(delivery_in.delivery_id, session)

    return result


async def create_delivery_fact(session: AsyncSession, delivery_in: list[DeliveryFact]):
    delivery_id = delivery_in[0].delivery_id
    stmt = delete(DeliveryItemFact).where(DeliveryItemFact.delivery_id == delivery_id)
    await session.execute(stmt)
    await session.commit()

    try:
        for item in delivery_in:
            stmt = usual_insert(DeliveryItemFact).values(**item.model_dump())
            await session.execute(stmt)
        await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка внешнего ключа или другие ограничения БД: {str(e)}",
        )

    asyncio.create_task(update_delivery_plan_fact(delivery_id=delivery_id))

    return {"status": status.HTTP_201_CREATED, "detail": "data fact created"}


async def get_delivery_differences(session: AsyncSession, delivery_id: uuid.UUID):
    stmt = select(Delivery).where(Delivery.id == delivery_id)
    result = await session.execute(stmt)
    find_delivery = result.scalar_one_or_none()
    if find_delivery is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"приобретение с id {delivery_id} не найдено в базе",
        )

    stmt = (
        select(
            DeliveryItemPlanFact.delivery_id,
            DeliveryItemPlanFact.product_id,
            DeliveryItemPlanFact.productpack_id,
            DeliveryItemPlanFact.producedate,
            DeliveryItemPlanFact.cis,
            DeliveryItemPlanFact.quantityplan,
            DeliveryItemPlanFact.quantityfact,
        )
        .where(DeliveryItemPlanFact.delivery_id == delivery_id)
        .where(DeliveryItemPlanFact.quantityplan != DeliveryItemPlanFact.quantityfact)
    )

    result = await session.execute(stmt)
    return result.mappings().all()


async def get_delivery_fact(session: AsyncSession, delivery_id: uuid.UUID):
    stmt = select(Delivery).where(Delivery.id == delivery_id)
    result = await session.execute(stmt)
    find_delivery = result.scalar_one_or_none()
    if find_delivery is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"приобретение с id {delivery_id} не найдено в базе",
        )

    if find_delivery.status != DocumentStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"приобретение с id {delivery_id} не в статусе Принято",
        )

    stmt = (
        select(DeliveryItemPlanFact.delivery_id)
        .where(DeliveryItemPlanFact.delivery_id == delivery_id)
        .where(DeliveryItemPlanFact.quantityplan != DeliveryItemPlanFact.quantityfact)
    )

    result = await session.execute(stmt)
    items = result.all()

    if items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"приобретение с id {delivery_id} содержит расхождение плана и факта."
            f" Текущмй статус приобретения {find_delivery.status.value}",
        )

    stmt = select(
        DeliveryItemPlanFact.delivery_id,
        DeliveryItemPlanFact.product_id,
        DeliveryItemPlanFact.productpack_id,
        DeliveryItemPlanFact.producedate,
        DeliveryItemPlanFact.cis,
        DeliveryItemPlanFact.quantityfact.label("quantity"),
    ).where(DeliveryItemPlanFact.delivery_id == delivery_id)

    result = await session.execute(stmt)
    return result.mappings().all()
