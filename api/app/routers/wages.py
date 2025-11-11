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
		where.append("(c.name ILIKE :county OR w.county ILIKE :county)")
	if year:
		params["year"] = year
		where.append("w.year = :year")
	where_sql = f"WHERE {' AND '.join(where)}" if where else ""

	queries = [
		f"""
		SELECT COALESCE(c.name, w.county) AS county, w.year::int AS year, w.average_wage::float AS average_wage
		FROM wages w
		LEFT JOIN counties c ON w.county_id = c.id
		{where_sql}
		ORDER BY county, year
		LIMIT :limit
		""",
		f"""
		SELECT w.county AS county, w.year::int AS year, w.average_wage::float AS average_wage
		FROM wages w
		{where_sql}
		ORDER BY county, year
		LIMIT :limit
		""",
	]
	rows = try_queries(queries, params)
	return [{"county": r.county, "year": int(r.year), "average_wage": float(r.average_wage)} for r in rows]


