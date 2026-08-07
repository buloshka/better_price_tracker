from typing import AsyncGenerator

import redis.asyncio as aioredis

from src.config import settings


redis_pool = aioredis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)

redis_factory = aioredis.Redis(connection_pool=redis_pool)


async def get_redis_session() -> AsyncGenerator[aioredis.Redis, None]:
    async with redis_factory.client() as session:
        yield session
