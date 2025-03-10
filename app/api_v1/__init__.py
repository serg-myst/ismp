from fastapi import APIRouter

from .organization.views import router as organization_router

router = APIRouter()
router.include_router(router=organization_router, prefix="/organizations")
