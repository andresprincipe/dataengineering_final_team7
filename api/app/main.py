from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, counties, enforcements, wages
from .reports import overview
from .deps import get_settings


def create_app() -> FastAPI:
	settings = get_settings()
	app = FastAPI(
		title=settings.API_TITLE,
		version=settings.API_VERSION,
		docs_url="/docs",
		redoc_url="/redoc",
	)

	# CORS (open by default; adjust via env if needed)
	app.add_middleware(
		CORSMiddleware,
		allow_origins=[o.strip() for o in settings.ALLOW_ORIGINS.split(",")] if settings.ALLOW_ORIGINS else ["*"],
		allow_credentials=True,
		allow_methods=[m.strip() for m in settings.ALLOW_METHODS.split(",")] if settings.ALLOW_METHODS else ["*"],
		allow_headers=[h.strip() for h in settings.ALLOW_HEADERS.split(",")] if settings.ALLOW_HEADERS else ["*"],
	)

	# Routers
	app.include_router(health.router, prefix="", tags=["health"])
	app.include_router(counties.router, prefix="/counties", tags=["counties"])
	app.include_router(enforcements.router, prefix="/enforcements", tags=["enforcements"])
	app.include_router(wages.router, prefix="/wages", tags=["wages"])
	app.include_router(overview.router, prefix="/report", tags=["reports"])

	@app.get("/", summary="Root")
	def root():
		return {"message": "Maryland Data Engineering API", "docs": "/docs"}

	return app


app = create_app()


