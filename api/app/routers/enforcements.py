from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import EnforcementSummary

router = APIRouter()

@router.get("", response_model=List[EnforcementSummary], summary="Enforcement counts by county/year")
def get_enforcement_summary(
    county: Optional[str] = Query(default=None),
    year: Optional[int] = Query(default=None, ge=1900, le=2100),
    source: Optional[str] = Query(default=None),
    limit: int = Query(default=500, ge=1, le=10000),
):
    params = {}
    where = []
    if county:
        params["county"] = f"%{county}%"
        where.append("(c.name ILIKE :county OR e.county ILIKE :county)")
    if year:
        params["year"] = year
        where.append("(EXTRACT(YEAR FROM e.action_date)::int = :year OR e.year = :year)")
    if source:
        params["source"] = source
        where.append("(e.source = :source)")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    params["limit"] = limit
    queries = [
        f"""
        SELECT
            COALESCE(c.name, e.county) AS county,
            EXTRACT(YEAR FROM e.action_date)::int AS year,
            COUNT(*)::int AS total_enforcements,
            MIN(e.source) AS source
        FROM enforcements e
        LEFT JOIN counties c ON e.county_id = c.id
        {where_sql}
        GROUP BY COALESCE(c.name, e.county), EXTRACT(YEAR FROM e.action_date)
        ORDER BY county, year
        LIMIT :limit
        """,
        f"""
        SELECT
            e.county AS county,
            e.year::int AS year,
            COUNT(*)::int AS total_enforcements,
            MIN(e.source) AS source
        FROM enforcements e
        {where_sql}
        GROUP BY e.county, e.year
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
