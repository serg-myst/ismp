from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.db_helper import db_helper
from fastapi import Depends
from . import crud
from .schemas import CheckingCreate

router = APIRouter(tags=["CheckCis"])


@router.post("/check/", status_code=status.HTTP_201_CREATED)
async def create_product(
    cis_in: list[CheckingCreate],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_check_cis(session=session, cis_in=cis_in)
