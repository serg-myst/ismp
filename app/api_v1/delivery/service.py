from sqlalchemy import select, insert, delete, update, func, literal, union_all
from datetime import datetime
from core.models.db_helper import db_helper
from .models import (
    DeliveryItemPlan,
    DeliveryItemFact,
    DeliveryItemPlanFact,
    Delivery,
    DeliveryStatusHistory,
    DocumentStatus,
)
from api_v1.cischecking.models import Checking


async def update_delivery_plan_fact(delivery_id):
    async with db_helper.session_dependency() as session:
        stmt = delete(DeliveryItemPlanFact).where(
            DeliveryItemPlanFact.delivery_id == delivery_id
        )
        await session.execute(stmt)
        await session.commit()

        plan_query = (
            select(
                DeliveryItemPlan.delivery_id,
                DeliveryItemPlan.product_id,
                DeliveryItemPlan.productpack_id,
                DeliveryItemPlan.producedate,
                Checking.cis.label("cis"),
                DeliveryItemPlan.quantity.label("quantityplan"),
                literal(None).label("quantityfact"),
            )
            .join(Checking, DeliveryItemPlan.checking_id == Checking.id)
            .where(DeliveryItemPlan.delivery_id == delivery_id)
        )

        fact_query = select(
            DeliveryItemFact.delivery_id,
            DeliveryItemFact.product_id,
            DeliveryItemFact.productpack_id,
            DeliveryItemFact.producedate,
            DeliveryItemFact.cis.label("cis"),
            literal(None).label("quantityplan"),
            DeliveryItemFact.quantity.label("quantityfact"),
        ).where(DeliveryItemFact.delivery_id == delivery_id)

        union_query = union_all(plan_query, fact_query).subquery()

        stmt = select(
            union_query.c.delivery_id,
            union_query.c.product_id,
            union_query.c.productpack_id,
            union_query.c.producedate,
            union_query.c.cis,
            func.coalesce(func.sum(union_query.c.quantityplan), 0).label(
                "quantityplan"
            ),
            func.coalesce(func.sum(union_query.c.quantityfact), 0).label(
                "quantityfact"
            ),
        ).group_by(
            union_query.c.delivery_id,
            union_query.c.product_id,
            union_query.c.productpack_id,
            union_query.c.producedate,
            union_query.c.cis,
        )

        result = await session.execute(stmt)
        items = []
        errors = 0
        for item in result:
            errors += 1 if item.quantityfact != item.quantityplan else 0
            items.append(
                {
                    "delivery_id": item.delivery_id,
                    "product_id": item.product_id,
                    "productpack_id": item.productpack_id,
                    "producedate": item.producedate,
                    "cis": item.cis,
                    "quantityplan": item.quantityplan,
                    "quantityfact": item.quantityfact,
                }
            )

        stmt = insert(DeliveryItemPlanFact).values(items)
        await session.execute(stmt)
        await session.commit()

        doc_status = (
            DocumentStatus.PLANFACT_ERROR if errors else DocumentStatus.ACCEPTED
        )

        stmt = (
            update(Delivery).where(Delivery.id == delivery_id).values(status=doc_status)
        )

        await session.execute(stmt)

        stmt = insert(DeliveryStatusHistory).values(
            delivery_id=delivery_id,
            status_date=datetime.now(),
            status=doc_status,
        )

        await session.execute(stmt)

        await session.commit()
