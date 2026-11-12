"""
Database connection layer.

One engine is created for the whole application (cheap to create, holds the
connection pool). Every request borrows a fresh `Session` from the pool via
the `get_db` dependency and returns it when the request finishes.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Parent class for every ORM model (see app/models/)."""


settings = get_settings()

# `pool_pre_ping=True` drops dead connections (e.g. after MySQL restarts),
# which avoids the classic "MySQL server has gone away" error.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # log every SQL statement while DEBUG is on (great for learning!)
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session per request.

    Endpoints receive it with `db: Session = Depends(get_db)`.
    The `finally` block guarantees the session is always returned to the pool.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
