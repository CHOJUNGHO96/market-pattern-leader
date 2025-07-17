from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class AsyncEngine:
    def __init__(self, config):
        self._config = config
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{config['POSTGRES_USER']}:{config['POSTGRES_PASSWORD']}@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_DB']}",
            future=True,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=30,
            connect_args={
                "server_settings": {
                    "timezone": "Asia/Seoul",
                    "search_path": self._config["POSTGRES_SCHEMA"],
                },
            },
        )
        self._session_factory = async_sessionmaker(
            self.engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def get_pg_session(
        self,
    ) -> AsyncIterator[AbstractAsyncContextManager[AsyncSession]]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
