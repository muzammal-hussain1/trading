import os
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.models import Base


def _async_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite"):
        return database_url
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed_url = urlsplit(database_url)
    query = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
    if query.get("sslmode") == "require":
        query["ssl"] = query.pop("sslmode")

    return urlunsplit(parsed_url._replace(query=urlencode(query)))


def _database_url_from_environment() -> str | None:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    if os.getenv("DB_HOST") is None:
        return "sqlite+aiosqlite:///./trading_api.db"

    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "defaultdb")
    sslmode = os.getenv("DB_SSLMODE", "require")

    if not all((host, user, password)):
        return None

    return (
        f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}"
        f"@{host}:{port}/{name}?sslmode={sslmode}"
    )


database_url = _database_url_from_environment()
engine: AsyncEngine | None = (
    create_async_engine(_async_database_url(database_url), pool_pre_ping=True)
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