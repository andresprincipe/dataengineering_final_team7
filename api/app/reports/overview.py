from typing import List, Optional
from fastapi import APIRouter, Query
from ..db import try_queries
from ..schemas import OverviewResponse, OverviewItem

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse, summary="Aggregated overview (wages + enforcement counts)")
def overview(
	county: Optional[str] = Query(default=None, description="Filter county (ILIKE)"),
	year: Optional[int] = Query(default=None, ge=1900, le=2100),
	limit: int = Query(default=1000, ge=1, le=10000),
):
	params = {"limit": limit}
	where = []
	if county:
		params["county"] = f"%{county}%"
		where.append("o.county ILIKE :county")
	if year:
		params["year"] = year
		where.append("o.year = :year")
	where_sql = f"WHERE {' AND '.join(where)}" if where else ""

	queries = [
		f"""
		SELECT county, year::int AS year, total_enforcements::int AS total_enforcements, average_wage::float AS average_wage
		FROM mv_overview_agg o
		{where_sql}
		ORDER BY county, year
		LIMIT :limit
		""",
		f"""
		WITH enforcement_counts AS (
			SELECT
				COALESCE(c.name, e.county) AS county,
				COALESCE(EXTRACT(YEAR FROM e.action_date)::int, e.year::int) AS year,
				COUNT(*)::int AS total_enforcements
			FROM enforcements e
			LEFT JOIN counties c ON e.county_id = c.id
			GROUP BY COALESCE(c.name, e.county), COALESCE(EXTRACT(YEAR FROM e.action_date)::int, e.year::int)
		),
		wages_norm AS (
			SELECT COALESCE(c.name, w.county) AS county, w.year::int AS year, w.average_wage::float AS average_wage
			FROM wages w
			LEFT JOIN counties c ON w.county_id = c.id
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
		""",
	]
	rows = try_queries(queries, params)
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


