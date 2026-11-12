"""
Pydantic schemas for the Author resource.

Schemas define the *shape of the JSON* that goes in and out of the API.
They are deliberately separate from the SQLAlchemy models:
  - Models   = how data is stored  (database world)
  - Schemas  = how data is shipped (HTTP world)
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthorBase(BaseModel):
    """Fields shared by create and update requests."""

    first_name: str = Field(min_length=1, max_length=50, examples=["George"])
    last_name: str = Field(min_length=1, max_length=50, examples=["Orwell"])


class AuthorCreate(AuthorBase):
    """Body of `POST /authors`."""


class AuthorUpdate(AuthorBase):
    """Body of `PUT /authors/{author_id}`."""


class AuthorResponse(AuthorBase):
    """What the API returns for every author. `model_config` lets Pydantic
    read the fields straight from an SQLAlchemy model object."""

    model_config = ConfigDict(from_attributes=True)

    author_id: int
    created_at: datetime
    updated_at: datetime


class AuthorListResponse(BaseModel):
    """Envelope for `GET /authors` so we can add pagination info later."""

    total: int
    items: list[AuthorResponse]
