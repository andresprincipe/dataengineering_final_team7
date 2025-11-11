from typing import Optional, List
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
	status: str = "ok"
	db_connected: bool
	version: str


class County(BaseModel):
	id: Optional[int] = None
	name: str
	fips_code: Optional[str] = Field(default=None, alias="fips")


class EnforcementSummary(BaseModel):
	county: str
	year: int
	total_enforcements: int
	source: Optional[str] = None


class Wage(BaseModel):
	county: str
	year: int
	average_wage: float


class OverviewItem(BaseModel):
	county: str
	year: int
	total_enforcements: int
	average_wage: Optional[float] = None


class OverviewResponse(BaseModel):
	items: List[OverviewItem]
	count: int


