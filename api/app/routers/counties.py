from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import County

router = APIRouter()

@router.get("", response_model=List[County], summary="List counties")
def list_counties(q: Optional[str] = Query(default=None), limit: int = Query(default=1000, ge=1, le=10000)):
    params = {"limit": limit}
    where = []
    if q:
        params["q"] = f"%{q}%"
        where.append("(c.name ILIKE :q)")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    queries = [
        f"""
        SELECT c.id AS id, c.name AS name, NULL::text AS state
        FROM counties c
        {where_sql}
        ORDER BY c.name
        LIMIT :limit
        """
    ]
    rows = try_queries(queries, params)
    return [{"id": r.id, "name": r.name, "state": getattr(r, "state", None)} for r in rows]
