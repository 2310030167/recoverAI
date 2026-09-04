from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_database_connection
from app.core.redis import check_redis_connection
from app.schemas import HealthResponse, DetailedHealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def get_v1_health() -> dict:
    """
    API v1 Health check endpoint.
    """
    return {
        "status": "ok",
        "service": "recoverai-api",
        "version": settings.APP_VERSION
    }


@router.get("/detailed", response_model=DetailedHealthResponse)
async def get_detailed_health() -> dict:
    """
    API v1 Detailed readiness & health check endpoint verifying
    PostgreSQL database and Redis infrastructure connectivity.
    """
    db_status = await check_database_connection()
    redis_status = await check_redis_connection()

    overall_status = "ok" if (
        db_status.get("status") in ["connected", "unknown"] and 
        redis_status.get("status") in ["connected", "unknown"]
    ) else "degraded"

    return {
        "status": overall_status,
        "service": "recoverai-api",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": db_status,
        "redis": redis_status,
    }
