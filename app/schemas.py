from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_timestamp(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is not None:
        return value.astimezone(UTC).replace(tzinfo=None)
    return value


class SymbolCreate(BaseModel):
    symbol: str | None = Field(default=None, max_length=50)
    start_time: datetime | None = Field(default=None, alias="startTime")

    model_config = ConfigDict(populate_by_name=True)

    _normalize_start_time = field_validator("start_time")(_normalize_timestamp)


class SymbolUpdate(BaseModel):
    symbol: str | None = Field(default=None, max_length=50)
    start_time: datetime | None = Field(default=None, alias="startTime")

    model_config = ConfigDict(populate_by_name=True)

    _normalize_start_time = field_validator("start_time")(_normalize_timestamp)


class SymbolResponse(BaseModel):
    id: int
    symbol: str | None
    start_time: datetime | None = Field(alias="startTime")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CandleCreate(BaseModel):
    open_time: datetime | None = Field(default=None, alias="openTime")
    open: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    high: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    low: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    close: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    volume: Decimal | None = Field(default=None, max_digits=20, decimal_places=8)
    close_time: datetime | None = Field(default=None, alias="closeTime")
    quote_volume: Decimal | None = Field(
        default=None, alias="quoteVolume", max_digits=20, decimal_places=8
    )
    trades: int | None = None
    percentage: Decimal | None = Field(
        default=None, max_digits=10, decimal_places=3
    )
    symbol: str | None = Field(default=None, max_length=50)
    timeframe: str | None = Field(default=None, max_length=20)

    model_config = ConfigDict(populate_by_name=True)

    _normalize_open_time = field_validator("open_time")(_normalize_timestamp)
    _normalize_close_time = field_validator("close_time")(_normalize_timestamp)


class CandleUpdate(CandleCreate):
    pass


class CandleResponse(BaseModel):
    id: int
    open_time: datetime | None = Field(alias="openTime")
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    volume: Decimal | None
    close_time: datetime | None = Field(alias="closeTime")
    quote_volume: Decimal | None = Field(alias="quoteVolume")
    trades: int | None
    percentage: Decimal | None
    symbol: str | None
    timeframe: str | None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)