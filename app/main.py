from fastapi import FastAPI

from app.api.api_v1.api import api_router
from app.core.config import settings

from app.db.session import engine
from app.db import Base


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)