from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from .schemas import Delivery as DeliverySchemas
from .models import Delivery


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
