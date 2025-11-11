# api/app/routers/wages.py
from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import Wage

router = APIRouter()

@router.get("", response_model=List[Wage], summary="Average wage per county/year")
def list_wages(
    county: Optional[str] = Query(default=None, description="County name (ILIKE)"),
    year: Optional[int] = Query(default=None, ge=1900, le=2100),
    limit: int = Query(default=1000, ge=1, le=10000),
):
    params = {"limit": limit}
    where = []

    if county:
        params["county"] = f"%{county}%"
        where.append("(c.county_name ILIKE :county OR c.name ILIKE :county OR w.county ILIKE :county)")
    if year:
        params["year"] = year
        where.append("w.year = :year")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    queries = [
        f"""
        SELECT
            COALESCE(c.county_name, c.name) AS county,
            w.year::int                      AS year,
            w.wage_for_county::float         AS wage_for_county
        FROM wage_per_county w
        LEFT JOIN counties c ON c.id = w.county_id
        {where_sql}
        ORDER BY county, year
        LIMIT :limit
        """,
        f"""
        SELECT
            COALESCE(c.county_name, c.name, w.county) AS county,
            w.year::int                               AS year,
            w.wage_for_county::float                  AS wage_for_county
        FROM wages w
        LEFT JOIN counties c ON c.id = w.county_id
        {where_sql}
        ORDER BY county, year
        LIMIT :limit
        """,
        f"""
        SELECT
            COALESCE(c.county_name, c.name, w.county) AS county,
            w.year::int                               AS year,
            w.average_wage::float                     AS wage_for_county
        FROM wages w
        LEFT JOIN counties c ON c.id = w.county_id
        {where_sql}
        ORDER BY county, year
        LIMIT :limit
        """,
    ]

    rows = try_queries(queries, params)
    return [
        {
            "county": r.county,
            "year": int(r.year),
            "average_wage": float(getattr(r, "wage_for_county")),  
        }
        for r in rows
    ]
