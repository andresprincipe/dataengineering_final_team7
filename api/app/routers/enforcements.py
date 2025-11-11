from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import EnforcementSummary

router = APIRouter()

@router.get("", response_model=List[EnforcementSummary], summary="Enforcement counts by county/year")
def get_enforcement_summary(
    county: Optional[str] = Query(default=None, description="County name (ILIKE)"),
    year: Optional[int] = Query(default=None, ge=1900, le=2100),
    source: Optional[str] = Query(default=None, description="Data source filter, e.g., 'air' or 'water'"),
    limit: int = Query(default=500, ge=1, le=10000),
):
    params = {"limit": limit}
    where = []

    if county:
        params["county"] = f"%{county}%"
        where.append("(c.county_name ILIKE :county OR COALESCE(e.county, '') ILIKE :county)")

    if year:
        params["year"] = year
        where.append("(COALESCE(EXTRACT(YEAR FROM e.action_date)::int, e.year::int) = :year)")

    if source:
        params["source"] = source.lower()
        where.append("(LOWER(e.source) = :source)")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    queries = [
        f"""
        SELECT
            COALESCE(c.county_name, e.county) AS county,
            COALESCE(EXTRACT(YEAR FROM e.action_date)::int, e.year::int) AS year,
            COUNT(*)::int AS total_enforcements,
            MIN(LOWER(e.source)) AS source
        FROM enforcements e
        LEFT JOIN counties c ON c.county_id = e.county_id
        {where_sql}
        GROUP BY COALESCE(c.county_name, e.county), COALESCE(EXTRACT(YEAR FROM e.action_date)::int, e.year::int)
        ORDER BY county, year
        LIMIT :limit
        """,
        f"""
        SELECT
            e.county AS county,
            COALESCE(EXTRACT(YEAR FROM e.action_date)::int, e.year::int) AS year,
            COUNT(*)::int AS total_enforcements,
            MIN(LOWER(e.source)) AS source
        FROM enforcements e
        {where_sql}
        GROUP BY e.county, COALESCE(EXTRACT(YEAR FROM e.action_date)::int, e.year::int)
        ORDER BY county, year
        LIMIT :limit
        """,
    ]

    rows = try_queries(queries, params)
    return [
        {
            "county": r.county,
            "year": int(r.year),
            "total_enforcements": int(r.total_enforcements),
            "source": getattr(r, "source", None),
        }
        for r in rows
    ]
