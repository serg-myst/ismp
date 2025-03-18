from fastapi import status, HTTPException
from sqlalchemy import delete, insert, select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from .models import Checking, PackType
from .schemas import CheckingCreate, CisUnit
from typing import List
import uuid
import asyncio
from .service import start_checking


async def create_check_cis(
    session: AsyncSession,
    cis_in: List[CheckingCreate],
):
    if len(cis_in) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no data to verify!"
        )

    delivery_id = cis_in[0].delivery_id
    stmt = delete(Checking).where(Checking.delivery_id == delivery_id)
    await session.execute(stmt)
    await session.commit()

    stmt = insert(Checking).values([cis.dict() for cis in cis_in])

    await session.execute(stmt)
    await session.commit()

    asyncio.create_task(start_checking(delivery_id=delivery_id))

    return {
        "status": status.HTTP_201_CREATED,
        "detail": "транспортные упаковки успешно приняты к проверке",
    }


async def get_flat_list(session, delivery_id):
    base_query = select(
        Checking.id,
        Checking.parent_id,
        Checking.product_id,
        Checking.cis,
        Checking.status,
        Checking.produceddate,
        Checking.gtin,
        Checking.ownerinn,
        Checking.ownername,
        Checking.packagetype,
        Checking.quantity,
        Checking.checked,
        Checking.ownererror,
        Checking.statuserror,
    ).where(Checking.delivery_id == delivery_id)

    result = await session.execute(base_query)
    items = result.mappings().all()
    return [{**dict(item), "children": []} for item in items]


def build_tree(items, parent_id, use_unit):
    tree = []
    for item in items:
        if not use_unit:
            if item["packagetype"] == PackType.UNIT:
                continue
        if item["parent_id"] == parent_id:
            children = build_tree(items, item["id"], use_unit)
            if children:
                item["children"] = children
            tree.append(item)
    return tree


async def get_hierarchy(session: AsyncSession, delivery_id, use_unit):
    items = await get_flat_list(session, delivery_id)
    return build_tree(items, uuid.UUID(int=0), use_unit)


async def get_product_by_package(session: AsyncSession, delivery_id, package):
    stmt = (
        select(
            Checking.product_id,
            Checking.packagetype,
            Checking.produceddate,
            func.sum(
                case(
                    (Checking.packagetype == "UNIT", Checking.quantity),
                    else_=1,
                )
            ).label("total_quantity"),
        )
        .where(Checking.delivery_id == delivery_id)
        .where(Checking.packagetype == package)
        .group_by(Checking.product_id, Checking.packagetype, Checking.produceddate)
        .order_by(Checking.product_id, Checking.produceddate)
    )
    result: Result = await session.execute(stmt)
    items = result.mappings().all()
    return list(items)


async def get_units_by_cis(session: AsyncSession, cis_in: CisUnit):
    stmt = (
        select(Checking.id, Checking.packagetype)
        .where(Checking.delivery_id == cis_in.delivery_id)
        .where(Checking.cis == cis_in.cis)
    )
    result: Result = await session.execute(stmt)

    row = result.fetchone()
    if row:
        if row.packagetype == PackType.UNIT:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тип упаковки марки должна быть упаковка, не UNIT",
            )

        stmt = select(Checking).where(Checking.parent_id == row.id)
        result: Result = await session.execute(stmt)
        items = result.mappings().all()
        return list(items)
