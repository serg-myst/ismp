from fastapi import FastAPI
from api_v1 import router as router_v1
from config.config import settings

app = FastAPI()

app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
