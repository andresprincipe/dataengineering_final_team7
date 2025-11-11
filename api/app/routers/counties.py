from typing import List
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import County

router = APIRouter()


@router.get("", response_model=List[County], summary="List counties")
def list_counties(q: str | None = Query(default=None, description="Filter by county name substring")):
	params = {}
	queries = [
		"""
		SELECT id, name, fips_code AS fips
		FROM counties
		{where}
		ORDER BY name
		""".replace("{where}", "WHERE name ILIKE :q" if q else ""),
		"""
		SELECT NULL::int AS id, county AS name, NULL::text AS fips
		FROM wages
		{where}
		GROUP BY county
		ORDER BY county
		""".replace("{where}", "WHERE county ILIKE :q" if q else ""),
	]
	if q:
		params["q"] = f"%{q}%"
	rows = try_queries(queries, params)
	return [{"id": r.id, "name": r.name, "fips": getattr(r, "fips", None)} for r in rows]


