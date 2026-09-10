from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
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


app = FastAPI(title="Trading API", version="1.0.0", lifespan=lifespan)


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


@app.get("/api/v1/symbols", response_model=list[SymbolResponse])
async def list_symbols(
    session: AsyncSession = Depends(get_session),
) -> list[Symbol]:
    result = await session.scalars(select(Symbol).order_by(Symbol.id))
    return list(result)


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
