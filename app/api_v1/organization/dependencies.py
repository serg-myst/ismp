from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.db_helper import db_helper
from typing import Annotated
import uuid
from . import crud
from .schemas import Organization
from .models import Organization as OrganizationModel


async def get_organization_by_id_to_create(
    organization: Organization,
    session: AsyncSession = Depends(
        db_helper.session_dependency,
    ),
) -> Organization:
    organization = await crud.get_organization(
        session=session, organization_id=organization.id
    )

    if organization:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"id {organization.id} already exists",
        )
    return organization


async def get_organization_by_id(
    organization_id: Annotated[uuid.UUID, Path],
    session: AsyncSession = Depends(
        db_helper.session_dependency,
    ),
) -> OrganizationModel:

    organization = await crud.get_organization(
        session=session, organization_id=organization_id
    )

    if organization is not None:
        return organization

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"id {organization_id} not found!",
    )
