from redis.asyncio import Redis


async def init_redis_pool(host: str, port: int, password: str) -> Redis:
    return Redis(host=host, port=port, password=password)
