"""
Shared FastAPI dependencies.

Right now it is only the database session, but as the project grows you
would put authentication (`get_current_user`), pagination params, etc. here.
"""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield one database session per request and always close it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
