from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import County

router = APIRouter()

@router.get("", response_model=List[County], summary="List counties")
def list_counties(
    name: Optional[str] = Query(default=None),
    limit: int = Query(default=200, ge=1, le=10000),
):
    params = {"limit": limit}
    where = []
    if name:
        params["name"] = f"%{name}%"
        where.append("c.county_name ILIKE :name")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    rows = try_queries(
        [
            f"""
            SELECT c.county_id, c.county_name, c.state
            FROM counties c
            {where_sql}
            ORDER BY c.county_name
            LIMIT :limit
            """
        ],
        params,
    )
    return [{"county_id": r.county_id, "county_name": r.county_name, "state": r.state} for r in rows]
