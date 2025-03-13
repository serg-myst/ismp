from fastapi import APIRouter

from .organization.views import router as organization_router
from .product.views import router as product_router
from .delivery.views import router as delivery_router
from .cischecking.views import router as check_router

router = APIRouter()
router.include_router(router=organization_router, prefix="/organizations")
router.include_router(router=product_router, prefix="/products")
router.include_router(router=delivery_router, prefix="/deliveries")
router.include_router(router=check_router, prefix="/check-cis")
