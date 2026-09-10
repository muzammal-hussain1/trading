import os

from pymongo import ASCENDING, AsyncMongoClient
from pymongo.errors import CollectionInvalid, PyMongoError


mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
mongodb_database_name = os.getenv("MONGODB_DATABASE", "trading_api")
mongodb_client = AsyncMongoClient(
    mongodb_uri,
    serverSelectionTimeoutMS=2000,
)
mongodb_database = mongodb_client[mongodb_database_name]


async def initialize_mongodb() -> str:
    try:
        await mongodb_client.admin.command("ping")

        for collection_name in ("symbols", "candles"):
            try:
                await mongodb_database.create_collection(collection_name)
            except CollectionInvalid:
                pass

        await mongodb_database.symbols.create_index(
            [("symbol", ASCENDING)], name="symbol_index"
        )
        await mongodb_database.candles.create_index(
            [("symbol", ASCENDING), ("timeframe", ASCENDING), ("openTime", ASCENDING)],
            name="candle_lookup_index",
        )
        return "connected"
    except PyMongoError:
        return "unavailable"


async def check_mongodb_connection() -> str:
    try:
        await mongodb_client.admin.command("ping")
        return "connected"
    except PyMongoError:
        return "unavailable"


async def close_mongodb() -> None:
    await mongodb_client.close()