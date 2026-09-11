from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.models import Base


database_url = "sqlite+aiosqlite:///./trading_api.db"
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
        existing_columns = await connection.run_sync(
            lambda sync_connection: {
                column["name"]
                for column in inspect(sync_connection).get_columns("symbols")
            }
        )
        symbol_columns = {
            "status": "VARCHAR(20) NOT NULL DEFAULT 'TRADING'",
            "baseAsset": "VARCHAR(20)",
            "baseAssetPrecision": "INTEGER NOT NULL DEFAULT 8",
            "quoteAsset": "VARCHAR(20)",
            "quotePrecision": "INTEGER NOT NULL DEFAULT 8",
            "quoteAssetPrecision": "INTEGER NOT NULL DEFAULT 8",
            "baseCommissionPrecision": "INTEGER NOT NULL DEFAULT 8",
            "quoteCommissionPrecision": "INTEGER NOT NULL DEFAULT 8",
            "icebergAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "ocoAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "otoAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "opoAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "quoteOrderQtyMarketAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "allowTrailingStop": "BOOLEAN NOT NULL DEFAULT 1",
            "cancelReplaceAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "amendAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "pegInstructionsAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "isSpotTradingAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "isMarginTradingAllowed": "BOOLEAN NOT NULL DEFAULT 1",
            "defaultSelfTradePreventionMode": "VARCHAR(30) NOT NULL DEFAULT 'EXPIRE_MAKER'",
        }
        for column_name, column_definition in symbol_columns.items():
            if column_name not in existing_columns:
                await connection.execute(
                    text(
                        f'ALTER TABLE symbols ADD COLUMN "{column_name}" '
                        f"{column_definition}"
                    )
                )

        existing_candle_columns = await connection.run_sync(
            lambda sync_connection: {
                column["name"]
                for column in inspect(sync_connection).get_columns("candles")
            }
        )
        candle_columns = {
            "takerBaseAssetVolume": "NUMERIC(20, 8)",
            "takerQuoteAssetVolume": "NUMERIC(20, 8)",
        }
        for column_name, column_definition in candle_columns.items():
            if column_name not in existing_candle_columns:
                await connection.execute(
                    text(
                        f'ALTER TABLE candles ADD COLUMN "{column_name}" '
                        f"{column_definition}"
                    )
                )


async def check_database_connection() -> str:
    if engine is None:
        return "not_configured"

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return "connected"
    except SQLAlchemyError:
        return "unavailable"