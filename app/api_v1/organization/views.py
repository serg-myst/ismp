from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from .schemas import Organization, OrganizationUpdate
from core.models.db_helper import db_helper
from fastapi import Depends
from .dependencies import get_organization_by_id_to_create, get_organization_by_id

router = APIRouter(tags=["Работа с организациями"])


@router.get(
    "/",
    response_model=list[Organization],
    status_code=status.HTTP_200_OK,
    summary="Метод возвращает список организаций вместе с реквизитами",
)
async def get_organizations(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_organizations(session=session)


@router.post(
    "/",
    response_model=Organization,
    status_code=status.HTTP_201_CREATED,
    summary="метод создает новую организацию",
)
async def create_organization(
    organization_in: Organization = Depends(get_organization_by_id_to_create),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_organization(session, organization_in=organization_in)


@router.patch(
    "/{organization_id}/",
    response_model=Organization,
    summary="метод обновляет реквизиты организации",
)
async def update_organisation(
    organization_update: OrganizationUpdate,
    organisation: Organization = Depends(get_organization_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_organization(
        session=session,
        organization=organisation,
        organization_update=organization_update,
    )
