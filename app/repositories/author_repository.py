"""
Author repository - all database operations for authors live here.

Endpoints never talk to SQLAlchemy directly; they call the repository.
That keeps the endpoint code short and makes the queries easy to test
and reuse ("separation of concerns").

Note: `tb_authors` uses a **soft delete** - the `deleted_at` column.
Instead of removing rows we set `deleted_at = now()`, and every read
filters `deleted_at IS NULL`. The data is never lost.
"""
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorUpdate


def get_all(db: Session, *, search: str | None = None, skip: int = 0, limit: int = 100) -> tuple[list[Author], int]:
    """Return (authors, total). `search` matches first or last name."""
    query = select(Author).where(Author.deleted_at.is_(None))

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Author.first_name.ilike(pattern),
                Author.last_name.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    authors = db.scalars(query.order_by(Author.author_id).offset(skip).limit(limit)).all()
    return list(authors), total


def get_by_id(db: Session, author_id: int) -> Author | None:
    """Fetch one alive author, or None if it does not exist (or was deleted)."""
    return db.scalar(
        select(Author).where(Author.author_id == author_id, Author.deleted_at.is_(None))
    )


def create(db: Session, data: AuthorCreate) -> Author:
    """Insert a new author row."""
    author = Author(first_name=data.first_name, last_name=data.last_name)
    db.add(author)
    db.commit()
    db.refresh(author)  # reload to pick up DB-generated values (author_id, timestamps)
    return author


def update(db: Session, author: Author, data: AuthorUpdate) -> Author:
    """Update an existing author row (already fetched and checked by the caller)."""
    author.first_name = data.first_name
    author.last_name = data.last_name
    db.commit()
    db.refresh(author)
    return author


def soft_delete(db: Session, author: Author) -> None:
    """Soft delete: stamp `deleted_at` instead of removing the row."""
    author.deleted_at = datetime.now(timezone.utc)
    db.commit()
