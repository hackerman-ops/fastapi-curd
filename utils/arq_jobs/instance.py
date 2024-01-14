from typing import Optional
from arq.connections import ArqRedis
from arq import create_pool
from arq.connections import RedisSettings

pool: Optional[ArqRedis] = None


async def create_redis_pool():
    pool = await create_pool(
        RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    )


async def close_redis_pool():
    pool.close()
