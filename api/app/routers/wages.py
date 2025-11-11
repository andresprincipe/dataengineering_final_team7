from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import Wage

router = APIRouter()


@router.get("", response_model=List[Wage], summary="Average wage per county/year")
def list_wages(
    county: Optional[str] = Query(default=None),
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
    q = f"""
    SELECT
        c.county_name AS county,
        w.year::int AS year,
        w.wage_for_county::float AS wage_for_county
    FROM wages_per_county w
    LEFT JOIN counties c ON c.county_id = w.county_id
    {where_sql}
    ORDER BY county, year
    LIMIT :limit
    """
    rows = try_queries([q], params)
    return [{"county": r.county, "year": int(r.year), "wage_for_county": float(r.wage_for_county)} for r in rows]
