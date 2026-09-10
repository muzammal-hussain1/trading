import os

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.models import Base


def _database_url_from_environment() -> str | None:
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./trading_api.db")


database_url = _database_url_from_environment()
engine: AsyncEngine | None = (
    create_async_engine(database_url, pool_pre_ping=True)
    if database_url
    else None
)
session_factory: async_sessionmaker[AsyncSession] | None = (
    async_sessionmaker(engine, expire_on_commit=False) if engine else None
)


async def get_session():
    if session_factory is None:
        raise RuntimeError("Database is not configured")

    async with session_factory() as session:
        yield session


async def initialize_database() -> None:
    if engine is None:
        return

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def check_database_connection() -> str:
    if engine is None:
        return "not_configured"

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "connected"
    except SQLAlchemyError:
        return "unavailable"