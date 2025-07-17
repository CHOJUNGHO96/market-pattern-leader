import pika
from dependency_injector import containers, providers

from api.v1.activities.container import ActivitiesContainer
from common import conf, setup_logging
from infrastructure.nosql.redis_client import init_redis_pool
from infrastructure.rdb.rdb_postgresql import AsyncEngine


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["api.v1.activities"],
    )

    _config = conf()
    config = providers.Configuration()
    config.from_dict(_config.dict())

    # log 의존성 주입
    logger = providers.Singleton(setup_logging)

    # PostgreSQL 리소스
    postgres_engine = providers.Resource(AsyncEngine, config=config)

    # Redis 리소스
    redis_client = providers.Resource(
        init_redis_pool,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
    )

    # RabbitMQ 리소스
    rabbitmq_connection = providers.Factory(
        pika.BlockingConnection,
        pika.ConnectionParameters(
            host=config()["RABBITMQ_HOST"],
            port=config()["RABBITMQ_PORT"],
            credentials=pika.PlainCredentials(config()["RABBITMQ_USER"], config()["RABBITMQ_PASSWORD"]),
        ),
    )

    # Activities container
    activities_container = providers.Container(
        ActivitiesContainer,
        config=config,
        logger=logger,
        postgres_engine=postgres_engine,
        redis_client=redis_client,
        rabbitmq_connection=rabbitmq_connection,
    )
