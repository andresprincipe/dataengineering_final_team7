## FastAPI Service (Maryland Data Engineering API)

This service exposes a FastAPI-based Web API to query PostgreSQL data and an aggregated overview combining wage and enforcement counts.

### Folder Structure

Final Project/
 ├── api/
 │    ├── app/
 │    ├── env.example
 │    └── .env               ← will be created manually
 ├── dags/
 ├── docker-compose.api.yml
 ├── docker-compose.api.snippet.yml
 ├── requirements.txt
 └── README.md

### Quickstart

1) Navigate to project directory

cd "/Users/xxx"

2) Create your .env file

cp api/env.example api/.env

```bash
docker compose build api
docker compose up -d api
```

3) Open Swagger UI:

- http://localhost:8088/docs

### Endpoints

- `GET /health` — API and DB health status
- `GET /counties` — List counties (supports `?q=` filter)
- `GET /enforcements` — Aggregated enforcement counts (filters: `county`, `year`, `source`, `limit`)
- `GET /wages` — Average wage per county/year (filters: `county`, `year`, `limit`)
- `GET /report/overview` — Combined wage + enforcement overview (filters: `county`, `year`, `limit`)

#### Example Requests

```bash
curl 'http://localhost:8088/health'

curl 'http://localhost:8088/counties?q=Mont'

curl 'http://localhost:8088/enforcements?county=Baltimore&year=2019'

curl 'http://localhost:8088/wages?county=Howard&year=2021'

curl 'http://localhost:8088/report/overview?county=Prince%20Georges&year=2020'
```

### Response Samples

- `/health`

```json
{ "status": "ok", "db_connected": true, "version": "1.0.0" }
```

- `/enforcements?county=Baltimore&year=2019`

```json
[
  { "county": "Baltimore County", "year": 2019, "total_enforcements": 128, "source": "Air" }
]
```

- `/report/overview?county=Howard&year=2021`

```json
{
  "items": [
    { "county": "Howard County", "year": 2021, "total_enforcements": 42, "average_wage": 71234.56 }
  ],
  "count": 1
}
```

### Environment Variables

You can set a full URL:

- `DATABASE_URL` — e.g. `postgresql+psycopg://postgres:postgres@postgres:5432/datawarehouse`

Or set parts (used if `DATABASE_URL` is not provided):

- `POSTGRES_HOST` (default: `postgres`)
- `POSTGRES_PORT` (default: `5432`)
- `POSTGRES_DB` (default: `datawarehouse`)
- `POSTGRES_USER` (default: `postgres`)
- `POSTGRES_PASSWORD` (default: `postgres`)

### Dockerfile

- Base: `python:3.11-slim`
- Entrypoint: uvicorn on port `8088`
- Loads `.env` automatically if present in the container

### docker-compose

Add this service to your `docker-compose.yml` (or merge as an override):

```yaml
api:
  build: ./api
  env_file: ./api/.env
  ports:
    - "8088:8088"
  depends_on:
    - postgres
    - airflow-webserver
  networks:
    - shared
```

If your stack uses a different network name, adjust `networks`.

### Airflow DAG (downstream)

Path: `dags/pipeline_api_and_refresh.py`

Tasks:
- `load_to_db` (PythonOperator): optional loader hook (uses env `DB_LOAD_SCRIPT` if provided)
- `refresh_materialized_view` (PostgresOperator): ensures `mv_overview_agg` exists and refreshes it
- `api_healthcheck` (PythonOperator): calls `http://api:8088/health`

Requirements:
- Airflow 2.8+
- Postgres connection id: `postgres_default` (configure in Airflow Connections)

### Notes on Schema Expectations

This API assumes the following tables or their equivalents exist:
- `counties(id, name, fips_code)`
- `enforcements(id, source, action_date, county_id?, county?, year?)`
- `wages(id, county_id?, county?, year, average_wage)`

For the overview, a materialized view `mv_overview_agg(county, year, total_enforcements, average_wage)` is expected. The DAG will create/refresh it if missing. If your column names differ, tell me and I’ll adjust the queries.


