from typing import Optional, Sequence, Any, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row
from sqlalchemy.exc import SQLAlchemyError
from .deps import get_settings, Settings

_engine: Optional[Engine] = None


def _build_database_url(settings: Settings) -> str:
	if settings.DATABASE_URL:
		return settings.DATABASE_URL
	user = settings.POSTGRES_USER
	password = settings.POSTGRES_PASSWORD
	host = settings.POSTGRES_HOST
	port = settings.POSTGRES_PORT
	db = settings.POSTGRES_DB
	return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def get_engine() -> Engine:
	global _engine
	if _engine is None:
		settings = get_settings()
		db_url = _build_database_url(settings)
		_engine = create_engine(
			db_url,
			pool_pre_ping=True,
			pool_size=5,
			max_overflow=10,
			future=True,
		)
	return _engine


def fetch_all(sql: str, params: Optional[Dict[str, Any]] = None) -> Sequence[Row]:
	engine = get_engine()
	with engine.connect() as conn:
		result = conn.execute(text(sql), params or {})
		return result.fetchall()


def fetch_one(sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Row]:
	engine = get_engine()
	with engine.connect() as conn:
		result = conn.execute(text(sql), params or {})
		row = result.fetchone()
		return row


def try_queries(queries: Sequence[str], params: Optional[Dict[str, Any]] = None) -> Sequence[Row]:
	last_err: Optional[Exception] = None
	for q in queries:
		try:
			return fetch_all(q, params)
		except SQLAlchemyError as e:
			last_err = e
	if last_err:
		raise last_err
	return []


