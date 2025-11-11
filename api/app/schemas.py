from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class HealthResponse(BaseModel):
    status: str = "ok"
    db_connected: bool
    version: str

class County(BaseModel):
    id: Optional[int] = Field(default=None, alias="county_id")
    name: str = Field(alias="county_name")
    state: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)

class EnforcementSummary(BaseModel):
    county: str
    year: int
    total_enforcements: int
    source: Optional[str] = None

class Wage(BaseModel):
    county: str = Field(description="County name (joined via County ID)")
    year: int
    average_wage: float = Field(alias="wage_for_county")
    model_config = ConfigDict(populate_by_name=True)

class OverviewItem(BaseModel):
    county: str
    year: int
    total_enforcements: int
    average_wage: Optional[float] = None

class OverviewResponse(BaseModel):
    items: List[OverviewItem]
    count: int
