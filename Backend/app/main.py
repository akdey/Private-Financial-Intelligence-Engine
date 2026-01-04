from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import get_settings
from app.core.database import engine, Base
from app.core.logging_config import setup_logging
from app.core.middleware import AuthenticationMiddleware

from app.features.auth.router import router as auth_router
from app.features.transactions.router import router as transactions_router
from app.features.sync.router import router as sync_router
from app.features.dashboard.router import router as dashboard_router
from app.features.sync.models import SyncLog 

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT in ["local", "development"]:
        logger.info(f"Environment: {settings.ENVIRONMENT}. Ensuring tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        logger.info(f"Environment: {settings.ENVIRONMENT}. Skipping table creation.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(AuthenticationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(transactions_router, prefix=f"{settings.API_V1_STR}/transactions", tags=["transactions"])
app.include_router(sync_router, prefix=f"{settings.API_V1_STR}/sync", tags=["sync"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Welcome to PFIE - Private Financial Intelligence Engine"}
