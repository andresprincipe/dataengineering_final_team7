from typing import Optional, List
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
	status: str = "ok"
	db_connected: bool
	version: str

class County(BaseModel):
    id: Optional[int] = Field(default=None, alias="county_id")
    name: str = Field(alias="county_name")
    state: str

    class Config:
        populate_by_name = True


class EnforcementSummary(BaseModel):
    county: str
    year: int
    total_enforcements: int
    source: Optional[Literal["air", "water"]] = None


class Wage(BaseModel):
    county: str = Field(description="County name (joined via County ID)")
    year: int
    average_wage: int = Field(alias="wage_for_county")

    class Config:
        populate_by_name = True



class OverviewItem(BaseModel):
	county: str
	year: int
	total_enforcements: int
	average_wage: Optional[int] = None


class OverviewResponse(BaseModel):
	items: List[OverviewItem]
	count: int


