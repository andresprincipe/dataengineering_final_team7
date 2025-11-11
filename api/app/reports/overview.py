from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import OverviewResponse, OverviewItem

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse, summary="Aggregated overview (wages + enforcement counts)")
def overview(
    county: Optional[str] = Query(default=None),
    year: Optional[int] = Query(default=None, ge=1900, le=2100),
    limit: int = Query(default=1000, ge=1, le=10000),
):
    params = {"limit": limit}
    wh = []
    if county:
        params["county"] = f"%{county}%"
        wh.append("o.county ILIKE :county")
    if year:
        params["year"] = year
        wh.append("o.year = :year")
    where_sql = f"WHERE {' AND '.join(wh)}" if wh else ""

    q_mv = f"""
    SELECT
        county,
        year::int AS year,
        total_enforcements::int AS total_enforcements,
        average_wage::float AS average_wage
    FROM mv_overview_agg o
    {where_sql}
    ORDER BY county, year
    LIMIT :limit
    """

    q_fallback = f"""
    WITH air AS (
        SELECT
            c.county_name AS county,
            NULLIF(substring(a.achieved_date FROM '^[0-9]{{4}}'), '')::int AS year
        FROM air_enforcements_md a
        LEFT JOIN counties c ON c.county_id = a.county_id
    ),
    water AS (
        SELECT
            c.county_name AS county,
            NULLIF(substring(w.case_closed FROM '^[0-9]{{4}}'), '')::int AS year
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
      ON e.county = w.county AND e.year = w.year
    {where_sql.replace('o.', '')}
    ORDER BY county, year
    LIMIT :limit
    """
    rows = try_queries([q_mv, q_fallback], params)
    items: List[OverviewItem] = []
    for r in rows:
        items.append(
            OverviewItem(
                county=r.county,
                year=int(r.year),
                total_enforcements=int(r.total_enforcements),
                average_wage=(float(r.average_wage) if getattr(r, "average_wage", None) is not None else None),
            )
        )
    return OverviewResponse(items=items, count=len(items))
