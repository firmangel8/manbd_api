"""
Application entry point.

Run the development server from the project root with:
    uvicorn app.main:app --reload

Then open the interactive docs at:
    http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.models import Author  # noqa: F401  (import registers the model with Base)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup / shutdown hook.

    On startup we (1) create tables that do not exist yet and (2) run a tiny
    `SELECT 1` to fail fast if the database is unreachable or credentials
    are wrong - with a clear error instead of an error on every request.
    """
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)  # convenient for learning; use Alembic in production

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Could not connect to MySQL. Check the DB_* values in your `.env` file."
        ) from exc

    yield  # <-- the app runs while we are parked here


app = FastAPI(
    title=settings.APP_NAME,
    description="Starter kit demonstrating a clean, modular FastAPI architecture "
    "with a full CRUD example on the `authors` resource.",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount the v1 "blueprint" under /api/v1 -> /api/v1/authors/...
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Simple liveness probe."""
    return {"status": "ok", "app": settings.APP_NAME}
