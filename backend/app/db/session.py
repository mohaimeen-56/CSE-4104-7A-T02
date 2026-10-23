import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

_db_url = settings.DATABASE_URL
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif _db_url.startswith("postgresql://") and not _db_url.startswith("postgresql+"):
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# On Vercel serverless, /var/task is read-only; fallback to writable /tmp for SQLite
if _db_url.startswith("sqlite") and (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")):
    _db_url = "sqlite:////tmp/sales_dashboard.db"

_is_sqlite = _db_url.startswith("sqlite")

if _is_sqlite:
    engine = create_engine(
        _db_url,
        connect_args={"check_same_thread": False},
        echo=False,
        future=True,
    )
else:
    # PostgreSQL / Supabase — pool settings optimized for both servers and serverless functions (Vercel)
    engine = create_engine(
        _db_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,   # recycle connections every 30 min to avoid idle drops
        pool_pre_ping=True,  # verify connection before use (catches dropped connections)
        echo=False,
        future=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
