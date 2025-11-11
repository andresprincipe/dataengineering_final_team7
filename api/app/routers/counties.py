from fastapi import APIRouter, Query
from typing import List, Optional
from ..db import fetch_all
from ..schemas import County

router = APIRouter()

@router.get("/counties", response_model=List[County], summary="List all counties")
def list_counties(state: Optional[str] = Query(default=None, description="Filter by state abbr (e.g. MD)")):
    if state:
        rows = fetch_all("""
            SELECT county_id, county_name, state
            FROM counties
            WHERE state = :state
            ORDER BY county_name
        """, {"state": state})
    else:
        rows = fetch_all("""
            SELECT county_id, county_name, state
            FROM counties
            ORDER BY county_name
        """)
    return [County(**dict(r)) for r in rows]
