# Trading API

A minimal Python REST API built with FastAPI.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

By default, the API uses a local SQLite database at `./trading_api.db`. The
`symbols` and `candles` tables are created automatically when the API starts.

The default local database requires no Docker service.

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /` - API welcome message
- `GET /health` - Health check
- `GET /api/v1/markets` - List sample markets
- `GET /api/v1/quote/{symbol}` - Get sample quote
- `POST /api/v1/symbols` - Create a symbol
- `POST /api/v1/symbols/sync-binance` - Import and update symbols from Binance
- `GET /api/v1/symbols` - List symbols
- `GET /api/v1/symbols/by-status?status=TRADING` - List symbols by status
- `GET /api/v1/symbols/by-base-asset?baseAsset=ETH` - List symbols by base asset
- `GET /api/v1/symbols/{id}` - Get a symbol
- `PATCH /api/v1/symbols/{id}` - Update a symbol
- `DELETE /api/v1/symbols/{id}` - Delete a symbol
- `POST /api/v1/candles` - Create a candle
- `GET /api/v1/candles` - List candles
- `GET /api/v1/candles/{id}` - Get a candle
- `PATCH /api/v1/candles/{id}` - Update a candle
- `DELETE /api/v1/candles/{id}` - Delete a candle

The `/health` response reports `database: connected` when the configured
database is reachable or `unavailable` when the connection check fails.

## Docs

Open `http://localhost:8000/docs` in your browser after starting the server.
