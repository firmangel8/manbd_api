"""
API v1 "blueprint" (the FastAPI equivalent of a Flask Blueprint).

Each version of your API is an `APIRouter`. `main.py` includes it under
the `/api/v1` prefix, so URLs look like: `/api/v1/authors`.

To add a new resource (e.g. books), create `endpoints/books.py`,
build a router there, and register it in the list below. That's it.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import authors

api_router = APIRouter()

api_router.include_router(authors.router, prefix="/authors", tags=["Authors"])
