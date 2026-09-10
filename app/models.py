from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String
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


class Candle(Base):
    __tablename__ = "candles"

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
    trades: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percentage: Mapped[Decimal | None] = mapped_column(
        "percent", Numeric(10, 3), nullable=True
    )
    symbol: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timeframe: Mapped[str | None] = mapped_column(String(20), nullable=True)