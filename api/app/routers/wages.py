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
        where.append("c.county_name ILIKE :county")
    if year:
        params["year"] = year
        where.append("w.year = :year")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    q1 = f"""
        SELECT 
            c.county_name            AS county,
            w.year::int              AS year,
            w.wage_for_county::float AS average_wage
        FROM average_wage_per_county w
        JOIN counties c ON w.county_id = c.county_id
        {where_sql}
        ORDER BY county, year
        LIMIT :limit
    """

    q2 = f"""
        SELECT 
            c.county_name            AS county,
            w.year::int              AS year,
            w.wage_for_county::float AS average_wage
        FROM wage_per_county w
        JOIN counties c ON w.county_id = c.county_id
        {where_sql}
        ORDER BY county, year
        LIMIT :limit
    """

    q3 = f"""
        SELECT 
            COALESCE(c.county_name, w.county) AS county,
            w.year::int                        AS year,
            COALESCE(w.wage_for_county, w.average_wage)::float AS average_wage
        FROM wages w
        LEFT JOIN counties c ON w.county_id = c.county_id
        {where_sql.replace('c.county_name', 'COALESCE(c.county_name, w.county)')}
        ORDER BY county, year
        LIMIT :limit
    """

    rows = try_queries([q1, q2, q3], params)
    return [
        {"county": r.county, "year": int(r.year), "average_wage": float(r.average_wage)}
        for r in rows
    ]
