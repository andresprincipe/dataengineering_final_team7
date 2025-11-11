from fastapi import APIRouter
from ..db import get_engine
from ..deps import get_settings
from ..schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check for API and DB")
def health():
	engine = get_engine()
	ok = False
	try:
		with engine.connect() as conn:
			conn.exec_driver_sql("SELECT 1")
		ok = True
	except Exception:
		ok = False
	settings = get_settings()
	return HealthResponse(status="ok" if ok else "degraded", db_connected=ok, version=settings.API_VERSION)


