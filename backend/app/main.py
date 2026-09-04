import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.redis import init_redis, close_redis
from app.api.router import api_router
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager handling startup and shutdown tasks.
    """
    logger.info(f"Starting {settings.APP_NAME} API v{settings.APP_VERSION} [{settings.APP_ENV}]")
    await init_redis()
    yield
    await close_redis()
    logger.info(f"Shutdown {settings.APP_NAME} API complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RecoverAI — AI Revenue Recovery Platform Backend API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root Health Check Endpoint (Unversioned as required by spec)
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def root_health() -> dict:
    """
    Unversioned root health check endpoint.
    Returns:
        {
          "status": "ok",
          "service": "recoverai-api",
          "version": "0.1.0"
        }
    """
    return {
        "status": "ok",
        "service": "recoverai-api",
        "version": settings.APP_VERSION
    }


# Include Versioned API Routers under /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
