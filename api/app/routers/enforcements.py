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
    limit: int = Query(default=1000, ge=1, le=10000),
):
    params = {"limit": limit}
    wh = []
    if county:
        params["county"] = f"%{county}%"
        wh.append("(x.county ILIKE :county)")
    if year:
        params["year"] = year
        wh.append("x.year = :year")
    if source:
        params["source"] = source.lower()
        wh.append("x.source = :source")
    where_sql = f"WHERE {' AND '.join(wh)}" if wh else ""

    q = f"""
    WITH air AS (
        SELECT
            c.county_name AS county,
            NULLIF(substring(a.achieved_date FROM '^[0-9]{{4}}'), '')::int AS year,
            'air'::text AS source
        FROM air_enforcements_md a
        LEFT JOIN counties c ON c.county_id = a.county_id
    ),
    water AS (
        SELECT
            c.county_name AS county,
            NULLIF(substring(w.case_closed FROM '^[0-9]{{4}}'), '')::int AS year,
            'water'::text AS source
        FROM water_enforcements_md w
        LEFT JOIN counties c ON c.county_id = w.county_id
    ),
    unioned AS (
        SELECT * FROM air
        UNION ALL
        SELECT * FROM water
    ),
    x AS (
        SELECT county, year, source
        FROM unioned
        WHERE county IS NOT NULL AND year IS NOT NULL
    )
    SELECT
        x.county,
        x.year,
        COUNT(*)::int AS total_enforcements,
        MIN(x.source) AS source
    FROM x
    {where_sql}
    GROUP BY x.county, x.year
    ORDER BY x.county, x.year
    LIMIT :limit
    """
    rows = try_queries([q], params)
    return [
        {
            "county": r.county,
            "year": int(r.year),
            "total_enforcements": int(r.total_enforcements),
            "source": getattr(r, "source", None),
        }
        for r in rows
    ]
