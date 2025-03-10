from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from .models import Organization
from .schemas import Organization as Organization_Schemas
from .schemas import OrganizationUpdate as OrganizationUpdate


async def get_organizations(session: AsyncSession) -> list[Organization]:
    stmt = select(Organization).order_by(Organization.name)
    result: Result = await session.execute(stmt)
    items = result.scalars().all()
    return list(items)


async def create_organization(
    session: AsyncSession,
    organization_in: Organization_Schemas,
):
    item = Organization(**organization_in.model_dump())
    session.add(item)
    await session.commit()
    return item


async def get_organization(
    session: AsyncSession, organization_id: uuid.UUID
) -> Organization | None:
    return await session.get(Organization, organization_id)


async def update_organization(
    session: AsyncSession,
    organization: Organization,
    organization_update: OrganizationUpdate,
):
    for name, value in organization_update.model_dump(exclude_unset=True).items():
        setattr(organization, name, value)
        await session.commit()
        return organization
