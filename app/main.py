from contextlib import asynccontextmanager
from decimal import Decimal, ROUND_HALF_UP

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import check_database_connection, get_session, initialize_database
from app.models import Candle, Symbol
from app.schemas import (
    CandleCreate,
    CandleResponse,
    CandleUpdate,
    SymbolCreate,
    SymbolResponse,
    SymbolUpdate,
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_database()
    yield


app = FastAPI(title="Trading API", version="1.0.1", lifespan=lifespan)
BINANCE_REQUEST_TIMEOUT_SECONDS = 24 * 60 * 60


class MarketQuote(BaseModel):
    symbol: str
    price: float
    change_percent: float


@app.get("/")
async def root() -> dict:
    return {
        "message": "Trading API is running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "trading-api",
        "database": await check_database_connection(),
    }


@app.get("/api/v1/markets")
async def list_markets() -> dict:
    return {
        "markets": [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft"},
            {"symbol": "NVDA", "name": "NVIDIA"},
        ]
    }


@app.get("/api/v1/quote/{symbol}")
async def get_quote(symbol: str) -> MarketQuote:
    sample_prices = {
        "AAPL": 214.32,
        "MSFT": 428.15,
        "NVDA": 124.8,
    }

    price = sample_prices.get(symbol.upper(), 100.0)
    return MarketQuote(
        symbol=symbol.upper(),
        price=price,
        change_percent=1.25,
    )


@app.post(
    "/api/v1/symbols",
    response_model=SymbolResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_symbol(
    symbol_data: SymbolCreate,
    session: AsyncSession = Depends(get_session),
) -> Symbol:
    symbol = Symbol(**symbol_data.model_dump())
    session.add(symbol)
    await session.commit()
    await session.refresh(symbol)
    return symbol


@app.post("/api/v1/symbols/sync-binance")
async def sync_binance_symbols(
    session: AsyncSession = Depends(get_session),
) -> dict[str, int | str]:
    try:
        async with httpx.AsyncClient(timeout=BINANCE_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get("https://api.binance.com/api/v3/exchangeInfo")
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Binance exchangeInfo request failed: {error}",
        ) from error

    exchange_info = response.json()
    binance_symbols = exchange_info.get("symbols", [])
    synced_count = 0

    for binance_symbol in binance_symbols:
        symbol_name = binance_symbol.get("symbol")
        if not symbol_name:
            continue

        symbol = await session.scalar(
            select(Symbol).where(Symbol.symbol == symbol_name)
        )
        if symbol is None:
            symbol = Symbol(symbol=symbol_name)
            session.add(symbol)

        symbol.status = binance_symbol.get("status", "TRADING")
        symbol.base_asset = binance_symbol.get("baseAsset")
        symbol.base_asset_precision = binance_symbol.get("baseAssetPrecision", 8)
        symbol.quote_asset = binance_symbol.get("quoteAsset")
        symbol.quote_precision = binance_symbol.get("quotePrecision", 8)
        symbol.quote_asset_precision = binance_symbol.get("quoteAssetPrecision", 8)
        symbol.base_commission_precision = binance_symbol.get(
            "baseCommissionPrecision", 8
        )
        symbol.quote_commission_precision = binance_symbol.get(
            "quoteCommissionPrecision", 8
        )
        symbol.iceberg_allowed = binance_symbol.get("icebergAllowed", True)
        symbol.oco_allowed = binance_symbol.get("ocoAllowed", True)
        symbol.oto_allowed = binance_symbol.get("otoAllowed", True)
        symbol.opo_allowed = binance_symbol.get("opoAllowed", True)
        symbol.quote_order_qty_market_allowed = binance_symbol.get(
            "quoteOrderQtyMarketAllowed", True
        )
        symbol.allow_trailing_stop = binance_symbol.get("allowTrailingStop", True)
        symbol.cancel_replace_allowed = binance_symbol.get(
            "cancelReplaceAllowed", True
        )
        symbol.amend_allowed = binance_symbol.get("amendAllowed", True)
        symbol.peg_instructions_allowed = binance_symbol.get(
            "pegInstructionsAllowed", True
        )
        symbol.is_spot_trading_allowed = binance_symbol.get(
            "isSpotTradingAllowed", True
        )
        symbol.is_margin_trading_allowed = binance_symbol.get(
            "isMarginTradingAllowed", True
        )
        symbol.default_self_trade_prevention_mode = binance_symbol.get(
            "defaultSelfTradePreventionMode", "EXPIRE_MAKER"
        )
        synced_count += 1

    await session.commit()
    return {"source": "binance", "synced": synced_count}


@app.get("/api/v1/symbols", response_model=list[SymbolResponse])
async def list_symbols(
    session: AsyncSession = Depends(get_session),
) -> list[Symbol]:
    result = await session.scalars(select(Symbol).order_by(Symbol.id))
    return list(result)


@app.get(
    "/api/v1/symbols/by-quoteAsset",
    response_model=list[SymbolResponse],
)
async def list_symbols_by_quote_asset(
    quote_asset: str = Query(..., alias="quoteAsset", min_length=1),
    session: AsyncSession = Depends(get_session),
) -> list[Symbol]:
    result = await session.scalars(
        select(Symbol)
        .where(Symbol.quote_asset == quote_asset.upper())
        .order_by(Symbol.id)
    )
    return list(result)


@app.get(
    "/api/v1/symbols/by-status",
    response_model=list[SymbolResponse],
)
async def list_symbols_by_status(
    status_value: str = Query(..., alias="status", min_length=1),
    quote_asset: str | None = Query(None, alias="quoteAsset", min_length=1),
    session: AsyncSession = Depends(get_session),
) -> list[Symbol]:
    filters = [Symbol.status == status_value.upper()]
    if quote_asset:
        filters.append(Symbol.quote_asset == quote_asset.upper())

    result = await session.scalars(select(Symbol).where(*filters).order_by(Symbol.id))
    return list(result)


@app.post("/api/v1/candles/download-binance")
async def download_binance_candles(
    start_time: int = Query(1789136648000, alias="startTime", ge=0),
    interval: str = Query("1m", min_length=1),
    limit: int = Query(1000, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int | str]:
    symbols = await session.scalars(
        select(Symbol.symbol)
        .where(Symbol.quote_asset == "USDT", Symbol.status == "TRADING")
        .where(Symbol.symbol.is_not(None))
        .order_by(Symbol.symbol)
    )
    symbol_names = list(symbols)
    downloaded_symbols = 0
    inserted_candles = 0
    request_count = 0

    try:
        async with httpx.AsyncClient(timeout=BINANCE_REQUEST_TIMEOUT_SECONDS) as client:
            for symbol_name in symbol_names:
                symbol_start_time = start_time

                while True:
                    response = await client.get(
                        "https://api.binance.com/api/v3/klines",
                        params={
                            "symbol": symbol_name,
                            "interval": interval,
                            "startTime": symbol_start_time,
                            "limit": limit,
                        },
                    )
                    request_count += 1
                    response.raise_for_status()
                    klines = response.json()
                    if not klines:
                        break

                    candle_rows = [
                        {
                            "open_time": kline[0],
                            "open": Decimal(kline[1]),
                            "high": Decimal(kline[2]),
                            "low": Decimal(kline[3]),
                            "close": Decimal(kline[4]),
                            "volume": Decimal(kline[5]),
                            "close_time": kline[6],
                            "quote_volume": Decimal(kline[7]),
                            "trades": kline[8],
                            "taker_base_asset_volume": Decimal(kline[9]),
                            "taker_quote_asset_volume": Decimal(kline[10]),
                            "percent": (
                                ((Decimal(kline[4]) - Decimal(kline[3]))
                                 / (Decimal(kline[2]) - Decimal(kline[3]))
                                 * Decimal("100"))
                                .quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
                                if Decimal(kline[2]) != Decimal(kline[3])
                                else Decimal("0")
                            ),
                            "symbol": symbol_name,
                            "interval": interval,
                        }
                        for kline in klines
                    ]
                    if candle_rows:
                        statement = sqlite_insert(Candle).values(candle_rows)
                        statement = statement.on_conflict_do_nothing(
                            index_elements=["symbol", "opentime", "interval"]
                        )
                        result = await session.execute(statement)
                        await session.commit()
                        inserted_candles += result.rowcount or 0

                    next_start_time = klines[-1][6]
                    if next_start_time <= symbol_start_time:
                        break
                    symbol_start_time = next_start_time

                downloaded_symbols += 1
    except httpx.HTTPError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Binance klines request failed: {error}",
        ) from error

    return {
        "source": "binance",
        "symbols": downloaded_symbols,
        "candles": inserted_candles,
        "requests": request_count,
        "interval": interval,
    }


@app.get("/api/v1/symbols/{symbol_id}", response_model=SymbolResponse)
async def get_symbol(
    symbol_id: int,
    session: AsyncSession = Depends(get_session),
) -> Symbol:
    symbol = await session.get(Symbol, symbol_id)
    if symbol is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return symbol


@app.patch("/api/v1/symbols/{symbol_id}", response_model=SymbolResponse)
async def update_symbol(
    symbol_id: int,
    symbol_data: SymbolUpdate,
    session: AsyncSession = Depends(get_session),
) -> Symbol:
    symbol = await session.get(Symbol, symbol_id)
    if symbol is None:
        raise HTTPException(status_code=404, detail="Symbol not found")

    for field, value in symbol_data.model_dump(exclude_unset=True).items():
        setattr(symbol, field, value)

    await session.commit()
    await session.refresh(symbol)
    return symbol


@app.delete("/api/v1/symbols/{symbol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symbol(
    symbol_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    symbol = await session.get(Symbol, symbol_id)
    if symbol is None:
        raise HTTPException(status_code=404, detail="Symbol not found")

    await session.delete(symbol)
    await session.commit()


@app.post(
    "/api/v1/candles",
    response_model=CandleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_candle(
    candle_data: CandleCreate,
    session: AsyncSession = Depends(get_session),
) -> Candle:
    candle = Candle(**candle_data.model_dump())
    session.add(candle)
    await session.commit()
    await session.refresh(candle)
    return candle


@app.get("/api/v1/candles", response_model=list[CandleResponse])
async def list_candles(
    session: AsyncSession = Depends(get_session),
) -> list[Candle]:
    result = await session.scalars(select(Candle).order_by(Candle.id))
    return list(result)


@app.get("/api/v1/candles/{candle_id}", response_model=CandleResponse)
async def get_candle(
    candle_id: int,
    session: AsyncSession = Depends(get_session),
) -> Candle:
    candle = await session.get(Candle, candle_id)
    if candle is None:
        raise HTTPException(status_code=404, detail="Candle not found")
    return candle


@app.patch("/api/v1/candles/{candle_id}", response_model=CandleResponse)
async def update_candle(
    candle_id: int,
    candle_data: CandleUpdate,
    session: AsyncSession = Depends(get_session),
) -> Candle:
    candle = await session.get(Candle, candle_id)
    if candle is None:
        raise HTTPException(status_code=404, detail="Candle not found")

    for field, value in candle_data.model_dump(exclude_unset=True).items():
        setattr(candle, field, value)

    await session.commit()
    await session.refresh(candle)
    return candle


@app.delete("/api/v1/candles/{candle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candle(
    candle_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    candle = await session.get(Candle, candle_id)
    if candle is None:
        raise HTTPException(status_code=404, detail="Candle not found")

    await session.delete(candle)
    await session.commit()
