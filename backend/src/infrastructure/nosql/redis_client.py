import logging
from redis.exceptions import RedisError
from redis.asyncio import Redis


async def init_redis_pool(host: str, port: int, password: str) -> Redis:
    try:
        redis_client = Redis(host=host, port=port, password=password)
        # 연결 테스트
        await redis_client.ping()
        return redis_client
    except RedisError as e:
        logging.error(f"Redis 연결 실패: {e}")
        raise
