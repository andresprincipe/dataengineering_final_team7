# api/app/routers/enforcements.py
from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import EnforcementSummary

router = APIRouter()

@router.get("", response_model=List[EnforcementSummary], summary="Enforcement counts by county/year")
def get_enforcement_summary(
    county: Optional[str] = Query(default=None, description="County name (ILIKE)"),
    year: Optional[int] = Query(default=None, ge=1900, le=2100),
    source: Optional[str] = Query(default=None, description="Filter by 'air' or 'water'"),
    limit: int = Query(default=500, ge=1, le=10000),
):

    params = {"limit": limit}
    where = []
    name_filter = "(c.county_name ILIKE :county OR c.name ILIKE :county OR e.county ILIKE :county)"

    if county:
        params["county"] = f"%{county}%"
        where.append(name_filter)

    post_where = []
    if year:
        params["year"] = year
        post_where.append("yr = :year")
    if source:
        params["source"] = source.lower()
        post_where.append("src = :source")

    post_where_sql = f"WHERE {' AND '.join(post_where)}" if post_where else ""

    queries = [
        f"""
        WITH air AS (
            SELECT a.county_id, EXTRACT(YEAR FROM a.achieved_date)::int AS yr, 'air'   AS src
            FROM air_enforcements a
        ),
        water AS (
            SELECT w.county_id, EXTRACT(YEAR FROM w.enforcement_action_issued)::int AS yr, 'water' AS src
            FROM water_enforcements w
        ),
        all_enf AS (
            SELECT * FROM air
            UNION ALL
            SELECT * FROM water
        )
        SELECT
            COALESCE(c.county_name, c.name) AS county,
            e.yr                             AS year,
            COUNT(*)::int                    AS total_enforcements,
            MIN(e.src)                       AS source
        FROM all_enf e
        LEFT JOIN counties c ON c.id = e.county_id
        {f"WHERE {name_filter.replace('e.county', 'NULL')}" if county else ""}  -- 只对 counties 名称做模糊
        GROUP BY county, e.yr
        {post_where_sql}
        ORDER BY county, year
        LIMIT :limit
        """,
        f"""
        WITH air AS (
            SELECT a.county_id, a.year::int AS yr, 'air' AS src FROM air_enforcements a
        ),
        water AS (
            SELECT w.county_id, w.year::int AS yr, 'water' AS src FROM water_enforcements w
        ),
        all_enf AS (
            SELECT * FROM air
            UNION ALL
            SELECT * FROM water
        )
        SELECT
            COALESCE(c.county_name, c.name) AS county,
            e.yr                             AS year,
            COUNT(*)::int                    AS total_enforcements,
            MIN(e.src)                       AS source
        FROM all_enf e
        LEFT JOIN counties c ON c.id = e.county_id
        {f"WHERE {name_filter.replace('e.county', 'NULL')}" if county else ""}
        GROUP BY county, e.yr
        {post_where_sql}
        ORDER BY county, year
        LIMIT :limit
        """,
        f"""
        SELECT
            COALESCE(c.county_name, c.name, e.county) AS county,
            e.year::int                                AS year,
            COUNT(*)::int                              AS total_enforcements,
            MIN(LOWER(e.source))                       AS source
        FROM enforcements e
        LEFT JOIN counties c ON c.id = e.county_id
        {f"WHERE {name_filter}" if county else ""}
        GROUP BY COALESCE(c.county_name, c.name, e.county), e.year
        {post_where_sql}
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
