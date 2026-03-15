import redis.asyncio as redis
from typing import AsyncGenerator

REDIS_URL = "redis://localhost:6379"

pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

async def get_redis() -> AsyncGenerator:
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.close()