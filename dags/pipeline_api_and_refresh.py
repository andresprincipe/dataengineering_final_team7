from __future__ import annotations
import os
import subprocess
from datetime import datetime, timedelta
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


def _load_to_db_callable(**context):
    load_script = os.environ.get("DB_LOAD_SCRIPT")
    if load_script:
        result = subprocess.run(load_script, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    else:
        print("No DB_LOAD_SCRIPT provided; assuming upstream tasks loaded data.")


def _api_healthcheck_callable(**context):
    url = os.environ.get("API_HEALTH_URL", "http://api:8088/health")
    timeout = int(os.environ.get("API_HEALTH_TIMEOUT", "20"))
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    body = resp.json()
    if not body.get("db_connected"):
        raise RuntimeError(f"API unhealthy or DB disconnected: {body}")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="pipeline_api_and_refresh",
    description="Ensure DB loaded, refresh materialized view, then API healthcheck",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    load_to_db = PythonOperator(
        task_id="load_to_db",
        python_callable=_load_to_db_callable,
    )

    refresh_materialized_view = PostgresOperator(
        task_id="refresh_materialized_view",
        postgres_conn_id="postgres_default",
        sql="""
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_matviews WHERE schemaname = 'public' AND matviewname = 'mv_overview_agg'
    ) THEN
        CREATE MATERIALIZED VIEW public.mv_overview_agg AS
        WITH air AS (
            SELECT
                c.county_name AS county,
                NULLIF(substring(a.achieved_date FROM '^[0-9]{4}'), '')::int AS year
            FROM air_enforcements_md a
            LEFT JOIN counties c ON c.county_id = a.county_id
        ),
        water AS (
            SELECT
                c.county_name AS county,
                NULLIF(substring(w.case_closed FROM '^[0-9]{4}'), '')::int AS year
            FROM water_enforcements_md w
            LEFT JOIN counties c ON c.county_id = w.county_id
        ),
        enforcement_counts AS (
            SELECT county, year, COUNT(*)::int AS total_enforcements
            FROM (
                SELECT * FROM air
                UNION ALL
                SELECT * FROM water
            ) t
            WHERE county IS NOT NULL AND year IS NOT NULL
            GROUP BY county, year
        ),
        wages_norm AS (
            SELECT c.county_name AS county, w.year::int AS year, w.wage_for_county::float AS average_wage
            FROM wages_per_county w
            LEFT JOIN counties c ON c.county_id = w.county_id
        )
        SELECT
            COALESCE(w.county, e.county) AS county,
            COALESCE(w.year, e.year) AS year,
            COALESCE(e.total_enforcements, 0)::int AS total_enforcements,
            w.average_wage::float AS average_wage
        FROM wages_norm w
        FULL OUTER JOIN enforcement_counts e
            ON e.county = w.county AND e.year = w.year;
    END IF;
END $$;

REFRESH MATERIALIZED VIEW public.mv_overview_agg;
        """,
    )

    api_healthcheck = PythonOperator(
        task_id="api_healthcheck",
        python_callable=_api_healthcheck_callable,
    )

    load_to_db >> refresh_materialized_view >> api_healthcheck
