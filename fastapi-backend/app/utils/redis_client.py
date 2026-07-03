"""Redis client singleton wrapper."""

from __future__ import annotations

from typing import Any

import redis.asyncio as aioredis
from loguru import logger

from app.core.config import get_settings

_redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """Return a singleton async Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        try:
            await _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as exc:
            logger.error(f"Redis connection failed: {exc}")
            raise
    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis client connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


async def cache_get(key: str) -> str | None:
    """Get a value from Redis cache."""
    client = await get_redis_client()
    return await client.get(key)


async def cache_set(
    key: str, value: str, expire: int | None = None
) -> bool:
    """Set a value in Redis cache with optional TTL."""
    client = await get_redis_client()
    return await client.set(key, value, ex=expire)


async def cache_delete(key: str) -> bool:
    """Delete a key from Redis cache."""
    client = await get_redis_client()
    return await client.delete(key) > 0
