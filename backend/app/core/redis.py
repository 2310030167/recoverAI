from typing import Optional
from redis.asyncio import Redis, from_url
from app.core.config import settings
from app.core.logging import logger

redis_client: Optional[Redis] = None


async def init_redis() -> Optional[Redis]:
    """
    Initialize asynchronous Redis connection client.
    """
    global redis_client
    try:
        redis_client = from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=3.0,
            socket_connect_timeout=3.0,
        )
        logger.info(f"Initialized Redis client targeting {settings.REDIS_URL}")
        return redis_client
    except Exception as e:
        logger.warning(f"Failed to initialize Redis connection: {e}")
        return None


async def close_redis() -> None:
    """
    Close Redis client connection.
    """
    global redis_client
    if redis_client:
        await redis_client.aclose()
        logger.info("Closed Redis connection.")
        redis_client = None


async def check_redis_connection() -> dict:
    """
    Utility to verify Redis connectivity via PING.
    """
    global redis_client
    try:
        client = redis_client or from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=2.0,
        )
        pong = await client.ping()
        if pong:
            return {"status": "connected", "redis": "ok"}
    except Exception as e:
        logger.warning(f"Redis connectivity check failed: {e}")
        return {"status": "disconnected", "error": str(e)}

    return {"status": "unknown"}
