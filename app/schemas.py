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
    status: str = "TRADING"
    base_asset: str | None = Field(default=None, alias="baseAsset")
    base_asset_precision: int = Field(default=8, alias="baseAssetPrecision")
    quote_asset: str | None = Field(default=None, alias="quoteAsset")
    quote_precision: int = Field(default=8, alias="quotePrecision")
    quote_asset_precision: int = Field(default=8, alias="quoteAssetPrecision")
    base_commission_precision: int = Field(default=8, alias="baseCommissionPrecision")
    quote_commission_precision: int = Field(default=8, alias="quoteCommissionPrecision")
    iceberg_allowed: bool = Field(default=True, alias="icebergAllowed")
    oco_allowed: bool = Field(default=True, alias="ocoAllowed")
    oto_allowed: bool = Field(default=True, alias="otoAllowed")
    opo_allowed: bool = Field(default=True, alias="opoAllowed")
    quote_order_qty_market_allowed: bool = Field(default=True, alias="quoteOrderQtyMarketAllowed")
    allow_trailing_stop: bool = Field(default=True, alias="allowTrailingStop")
    cancel_replace_allowed: bool = Field(default=True, alias="cancelReplaceAllowed")
    amend_allowed: bool = Field(default=True, alias="amendAllowed")
    peg_instructions_allowed: bool = Field(default=True, alias="pegInstructionsAllowed")
    is_spot_trading_allowed: bool = Field(default=True, alias="isSpotTradingAllowed")
    is_margin_trading_allowed: bool = Field(default=True, alias="isMarginTradingAllowed")
    default_self_trade_prevention_mode: str = Field(
        default="EXPIRE_MAKER", alias="defaultSelfTradePreventionMode"
    )

    model_config = ConfigDict(populate_by_name=True)

    _normalize_start_time = field_validator("start_time")(_normalize_timestamp)


class SymbolUpdate(BaseModel):
    symbol: str | None = Field(default=None, max_length=50)
    start_time: datetime | None = Field(default=None, alias="startTime")
    status: str | None = None
    base_asset: str | None = Field(default=None, alias="baseAsset")
    base_asset_precision: int | None = Field(default=None, alias="baseAssetPrecision")
    quote_asset: str | None = Field(default=None, alias="quoteAsset")
    quote_precision: int | None = Field(default=None, alias="quotePrecision")
    quote_asset_precision: int | None = Field(default=None, alias="quoteAssetPrecision")
    base_commission_precision: int | None = Field(default=None, alias="baseCommissionPrecision")
    quote_commission_precision: int | None = Field(default=None, alias="quoteCommissionPrecision")
    iceberg_allowed: bool | None = Field(default=None, alias="icebergAllowed")
    oco_allowed: bool | None = Field(default=None, alias="ocoAllowed")
    oto_allowed: bool | None = Field(default=None, alias="otoAllowed")
    opo_allowed: bool | None = Field(default=None, alias="opoAllowed")
    quote_order_qty_market_allowed: bool | None = Field(default=None, alias="quoteOrderQtyMarketAllowed")
    allow_trailing_stop: bool | None = Field(default=None, alias="allowTrailingStop")
    cancel_replace_allowed: bool | None = Field(default=None, alias="cancelReplaceAllowed")
    amend_allowed: bool | None = Field(default=None, alias="amendAllowed")
    peg_instructions_allowed: bool | None = Field(default=None, alias="pegInstructionsAllowed")
    is_spot_trading_allowed: bool | None = Field(default=None, alias="isSpotTradingAllowed")
    is_margin_trading_allowed: bool | None = Field(default=None, alias="isMarginTradingAllowed")
    default_self_trade_prevention_mode: str | None = Field(
        default=None, alias="defaultSelfTradePreventionMode"
    )

    model_config = ConfigDict(populate_by_name=True)

    _normalize_start_time = field_validator("start_time")(_normalize_timestamp)


class SymbolResponse(BaseModel):
    id: int
    symbol: str | None
    start_time: datetime | None = Field(alias="startTime")
    status: str
    base_asset: str | None = Field(alias="baseAsset")
    base_asset_precision: int = Field(alias="baseAssetPrecision")
    quote_asset: str | None = Field(alias="quoteAsset")
    quote_precision: int = Field(alias="quotePrecision")
    quote_asset_precision: int = Field(alias="quoteAssetPrecision")
    base_commission_precision: int = Field(alias="baseCommissionPrecision")
    quote_commission_precision: int = Field(alias="quoteCommissionPrecision")
    iceberg_allowed: bool = Field(alias="icebergAllowed")
    oco_allowed: bool = Field(alias="ocoAllowed")
    oto_allowed: bool = Field(alias="otoAllowed")
    opo_allowed: bool = Field(alias="opoAllowed")
    quote_order_qty_market_allowed: bool = Field(alias="quoteOrderQtyMarketAllowed")
    allow_trailing_stop: bool = Field(alias="allowTrailingStop")
    cancel_replace_allowed: bool = Field(alias="cancelReplaceAllowed")
    amend_allowed: bool = Field(alias="amendAllowed")
    peg_instructions_allowed: bool = Field(alias="pegInstructionsAllowed")
    is_spot_trading_allowed: bool = Field(alias="isSpotTradingAllowed")
    is_margin_trading_allowed: bool = Field(alias="isMarginTradingAllowed")
    default_self_trade_prevention_mode: str = Field(alias="defaultSelfTradePreventionMode")

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
    taker_base_asset_volume: Decimal | None = Field(
        default=None, alias="takerBaseAssetVolume", max_digits=20, decimal_places=8
    )
    taker_quote_asset_volume: Decimal | None = Field(
        default=None, alias="takerQuoteAssetVolume", max_digits=20, decimal_places=8
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
    taker_base_asset_volume: Decimal | None = Field(alias="takerBaseAssetVolume")
    taker_quote_asset_volume: Decimal | None = Field(alias="takerQuoteAssetVolume")
    trades: int | None
    percentage: Decimal | None
    symbol: str | None
    timeframe: str | None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)