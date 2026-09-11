from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Symbol(Base):
    __tablename__ = "symbols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_time: Mapped[datetime | None] = mapped_column(
        "starttime", DateTime, nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="TRADING")
    base_asset: Mapped[str | None] = mapped_column("baseAsset", String(20))
    base_asset_precision: Mapped[int] = mapped_column("baseAssetPrecision", Integer, default=8)
    quote_asset: Mapped[str | None] = mapped_column("quoteAsset", String(20))
    quote_precision: Mapped[int] = mapped_column("quotePrecision", Integer, default=8)
    quote_asset_precision: Mapped[int] = mapped_column("quoteAssetPrecision", Integer, default=8)
    base_commission_precision: Mapped[int] = mapped_column("baseCommissionPrecision", Integer, default=8)
    quote_commission_precision: Mapped[int] = mapped_column("quoteCommissionPrecision", Integer, default=8)
    iceberg_allowed: Mapped[bool] = mapped_column("icebergAllowed", default=True)
    oco_allowed: Mapped[bool] = mapped_column("ocoAllowed", default=True)
    oto_allowed: Mapped[bool] = mapped_column("otoAllowed", default=True)
    opo_allowed: Mapped[bool] = mapped_column("opoAllowed", default=True)
    quote_order_qty_market_allowed: Mapped[bool] = mapped_column(
        "quoteOrderQtyMarketAllowed", default=True
    )
    allow_trailing_stop: Mapped[bool] = mapped_column("allowTrailingStop", default=True)
    cancel_replace_allowed: Mapped[bool] = mapped_column("cancelReplaceAllowed", default=True)
    amend_allowed: Mapped[bool] = mapped_column("amendAllowed", default=True)
    peg_instructions_allowed: Mapped[bool] = mapped_column("pegInstructionsAllowed", default=True)
    is_spot_trading_allowed: Mapped[bool] = mapped_column("isSpotTradingAllowed", default=True)
    is_margin_trading_allowed: Mapped[bool] = mapped_column("isMarginTradingAllowed", default=True)
    default_self_trade_prevention_mode: Mapped[str] = mapped_column(
        "defaultSelfTradePreventionMode", String(30), default="EXPIRE_MAKER"
    )


class Candle(Base):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint(
            "symbol", "opentime", "interval", name="uq_candles_symbol_open_time_interval"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    open_time: Mapped[datetime | None] = mapped_column(
        "opentime", DateTime, nullable=True
    )
    open: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8), nullable=True
    )
    high: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8), nullable=True
    )
    low: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8), nullable=True
    )
    close: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8), nullable=True
    )
    volume: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8), nullable=True
    )
    close_time: Mapped[datetime | None] = mapped_column(
        "closetime", DateTime, nullable=True
    )
    quote_volume: Mapped[Decimal | None] = mapped_column(
        "quotevolume", Numeric(20, 8), nullable=True
    )
    taker_base_asset_volume: Mapped[Decimal | None] = mapped_column(
        "takerBaseAssetVolume", Numeric(20, 8), nullable=True
    )
    taker_quote_asset_volume: Mapped[Decimal | None] = mapped_column(
        "takerQuoteAssetVolume", Numeric(20, 8), nullable=True
    )
    trades: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percentage: Mapped[Decimal | None] = mapped_column(
        "percent", Numeric(10, 3), nullable=True
    )
    symbol: Mapped[str | None] = mapped_column(String(50), nullable=True)
    interval: Mapped[str | None] = mapped_column("interval", String(20), nullable=True)