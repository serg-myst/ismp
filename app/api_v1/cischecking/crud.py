from fastapi import status
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Checking
from .schemas import CheckingCreate
from typing import List


async def create_check_cis(
    session: AsyncSession,
    cis_in: List[CheckingCreate],
):
    if len(cis_in) != 0:
        stmt = delete(Checking).where(Checking.delivery_id == cis_in[0].delivery_id)
        await session.execute(stmt)
        await session.commit()

    stmt = insert(Checking).values([cis.dict() for cis in cis_in])

    await session.execute(stmt)
    await session.commit()

    return {
        "status": status.HTTP_201_CREATED,
        "detail": "транспортные упаковки успешно приняты к проверке",
    }
