# Trading API

A minimal Python REST API built with FastAPI.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Set the PostgreSQL connection variables before starting the API. Do not commit
the real password or place it directly in source code.

```powershell
$env:DB_HOST = "pg-25f1b0f9-mh-crypto.i.aivencloud.com"
$env:DB_PORT = "17079"
$env:DB_NAME = "defaultdb"
$env:DB_USER = "avnadmin"
$env:DB_PASSWORD = "YOUR_PASSWORD"
$env:DB_SSLMODE = "require"
```

`DATABASE_URL` is also supported as a fallback for existing deployments.

The project also supports a local MongoDB database. MongoDB uses collections
instead of SQL tables. The API creates the `symbols` and `candles` collections
and their indexes when it starts.

Install and start MongoDB locally, then configure it if using non-default
values:

```powershell
docker compose up -d mongodb
$env:MONGODB_URI = "mongodb://localhost:27017"
$env:MONGODB_DATABASE = "trading_api"
```

After Docker Desktop is running, start the API with `uvicorn`. Its startup
routine creates the MongoDB collections and indexes automatically.

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
- `GET /api/v1/symbols` - List symbols
- `GET /api/v1/symbols/{id}` - Get a symbol
- `PATCH /api/v1/symbols/{id}` - Update a symbol
- `DELETE /api/v1/symbols/{id}` - Delete a symbol
- `POST /api/v1/candles` - Create a candle
- `GET /api/v1/candles` - List candles
- `GET /api/v1/candles/{id}` - Get a candle
- `PATCH /api/v1/candles/{id}` - Update a candle
- `DELETE /api/v1/candles/{id}` - Delete a candle

The `/health` response reports `database: connected` when PostgreSQL is
reachable, `not_configured` when `DATABASE_URL` is missing, or `unavailable`
when the connection check fails.

It also reports `mongodb: connected` after the local MongoDB collections and
indexes have been initialized.

## Docs

Open `http://localhost:8000/docs` in your browser after starting the server.
