# FastPipeline

A FastAPI service for defining, scheduling, and running ETL pipelines. Pipelines extract from CSV files or HTTP APIs, transform with domain-specific cleaners, and load results into PostgreSQL or CSV.

## Features

- **REST API** to create, list, run, and delete pipelines
- **Job tracking** with status, record counts, and error messages
- **Cron scheduling** via APScheduler (timezone: `Asia/Kuala_Lumpur`)
- **Sources**: CSV files, Open-Meteo weather API
- **Destinations**: PostgreSQL tables or CSV files under `data/transformed/`
- **Structured logging** to stderr and rotating JSONL files
- **Docker Compose** stack with PostgreSQL 15

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  FastAPI    │────▶│  ETL Engine  │────▶│  Postgres / CSV │
│  + Scheduler│     │  Extract →   │     │                 │
└─────────────┘     │  Transform → │     └─────────────────┘
                    │  Load        │
                    └──────────────┘
```

| Layer | Role |
| --- | --- |
| **Extract** | Read CSV (`source_type: CSV`) or call Open-Meteo (`source_type: API`) |
| **Transform** | Cleaners keyed by pipeline name: `orders`, `customers`, `products`, `weather` |
| **Load** | Write to a Postgres table or `./data/transformed/{name}-{job_id}.csv` |

## Project layout

```
FastPipeline/
├── app/
│   ├── main.py                 # FastAPI routes & lifespan
│   ├── models.py               # Pipelines & Jobs (SQLModel)
│   ├── database.py             # Postgres engine
│   ├── config.json             # Logging config
│   ├── requirements.txt
│   └── services/
│       ├── etl.py              # Pipeline runner
│       ├── scheduler.py        # Cron scheduling
│       ├── extract/extract.py
│       └── transform/          # Domain cleaners
├── data/
│   ├── raw/                    # Place source CSVs here
│   └── transformed/            # CSV load output
├── migrations/                 # Alembic
├── docker-compose.yml
└── Dockerfile
```

## Prerequisites

- Docker & Docker Compose
- A `.env` file in the project root (see below)

## Quick start

1. **Create a `.env` file** with Postgres credentials:

```env
DB_USER=pipeline
DB_PASSWORD=secret
DB_NAME=fastpipeline
```

2. **Start the stack:**

```bash
docker compose up --build
```

3. **Open the API:**

- App: [http://localhost:8000](http://localhost:8000)
- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: `GET /` → `{"status": "Connected to Database!"}`

Tables are created automatically on startup. Alembic migrations live under `migrations/` if you need schema versioning separately.

## API reference

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Database health check |
| `POST` | `/pipelines` | Create a pipeline (schedules it if `cron_expression` is set) |
| `GET` | `/pipelines` | List pipelines (`offset`, `limit` ≤ 100) |
| `GET` | `/pipelines/{pipe_id}` | Get a pipeline by ID |
| `DELETE` | `/pipelines/{pipe_id}` | Delete a pipeline and unschedule it |
| `POST` | `/pipelines/{pipe_id}/run` | Queue a job and run the pipeline in the background |
| `GET` | `/pipelines/{pipe_id}/jobs` | List jobs for a pipeline |
| `GET` | `/jobs/{job_id}` | Get job status |

### Pipeline body

```json
{
  "name": "orders",
  "source_type": "CSV",
  "source_config": { "path": "data/raw/orders.csv" },
  "destination_type": "postgres",
  "destination_config": { "table": "orders_clean" },
  "cron_expression": "0 2 * * *"
}
```

| Field | Notes |
| --- | --- |
| `name` | Selects the transformer: `orders`, `customers`, `products`, or `weather` |
| `source_type` | `CSV` or `API` |
| `source_config` | CSV: `{ "path": "..." }`. API/weather: `{ "url": "...", "params": { ... } }` |
| `destination_type` | `postgres` or `csv` |
| `destination_config` | Optional `{ "table": "..." }` for Postgres (defaults to `{name}-{job_id}`) |
| `cron_expression` | Optional 5-field cron string; omit for on-demand only |

### Job statuses

`pending` → `running` → `success` | `failed`

## Examples

### CSV → Postgres (orders)

Place a CSV at `data/raw/orders.csv`, then:

```bash
curl -X POST http://localhost:8000/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "orders",
    "source_type": "CSV",
    "source_config": { "path": "data/raw/orders.csv" },
    "destination_type": "postgres",
    "destination_config": { "table": "orders_clean" }
  }'
```

Run it:

```bash
curl -X POST http://localhost:8000/pipelines/{pipe_id}/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Weather API → CSV

```bash
curl -X POST http://localhost:8000/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weather",
    "source_type": "API",
    "source_config": {
      "url": "https://api.open-meteo.com/v1/forecast",
      "params": {
        "latitude": 3.14,
        "longitude": 101.69,
        "hourly": "temperature_2m,relativehumidity_2m,precipitation"
      }
    },
    "destination_type": "csv"
  }'
```

### Scheduled pipeline

Set `cron_expression` (e.g. `"0 */6 * * *"` for every 6 hours). On create, the pipeline is registered with the in-process scheduler. Deleting the pipeline removes the schedule.

## Transformers

| Pipeline name | Source | Cleaning highlights |
| --- | --- | --- |
| `customers` | CSV | Title-case names/countries, normalize email, coerce signup dates, fill nulls |
| `orders` | CSV | Normalize order dates, parse numeric `total_amount` |
| `products` | CSV | Title-case category, parse amounts |
| `weather` | Open-Meteo API | Hourly series with renamed fields (`temperature`, `humidity`, `precipitation`) |

## Logging

Configured in `app/config.json`:

- **stderr**: WARNING+ (simple format)
- **`logs/my_app.log.jsonl`**: DEBUG+ JSON lines, rotating (10 KB × 3 backups)

The `logs/` directory is mounted into the container via Compose.

## Development notes

- The Compose app service mounts the project at `/code` and runs Uvicorn with `--reload`.
- DB host inside Docker is `my-db` (see `app/database.py`); credentials come from `POSTGRES_*` env vars mapped from `.env`.
- CSV destination writes go to `./data/transformed/`. Ensure that path exists and is writable.
- Scheduler timezone is fixed to `Asia/Kuala_Lumpur`.

## Tech stack

Python 3.12 · FastAPI · SQLModel · PostgreSQL · Alembic · APScheduler · pandas · Open-Meteo · Docker
