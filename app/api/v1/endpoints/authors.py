"""
Authors CRUD endpoint (the "blueprint" for one resource).

An endpoint file keeps only HTTP concerns:
  - validate input (via Pydantic schemas)
  - call the repository for data work
  - choose the status code / raise HTTP errors

Business logic and SQL never appear here - see `repositories/`.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories import author_repository as repo
from app.schemas.author import AuthorCreate, AuthorListResponse, AuthorResponse, AuthorUpdate

router = APIRouter()


@router.get("", response_model=AuthorListResponse, summary="List all authors")
def list_authors(
    search: str | None = Query(default=None, description="Match first or last name"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> AuthorListResponse:
    """`GET /authors` - supports ?search=&skip=&limit= for pagination."""
    authors, total = repo.get_all(db, search=search, skip=skip, limit=limit)
    return AuthorListResponse(total=total, items=authors)


@router.get("/{author_id}", response_model=AuthorResponse, summary="Get one author")
def get_author(author_id: int, db: Session = Depends(get_db)) -> AuthorResponse:
    """`GET /authors/{id}` - 404 when the author does not exist."""
    author = repo.get_by_id(db, author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id {author_id} not found",
        )
    return author


@router.post(
    "",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an author",
)
def create_author(data: AuthorCreate, db: Session = Depends(get_db)) -> AuthorResponse:
    """`POST /authors` - body: {"first_name": "...", "last_name": "..."}"""
    return repo.create(db, data)


@router.put("/{author_id}", response_model=AuthorResponse, summary="Update an author")
def update_author(
    author_id: int, data: AuthorUpdate, db: Session = Depends(get_db)
) -> AuthorResponse:
    """`PUT /authors/{id}` - replaces first and last name."""
    author = repo.get_by_id(db, author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id {author_id} not found",
        )
    return repo.update(db, author, data)


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an author (soft delete)",
)
def delete_author(author_id: int, db: Session = Depends(get_db)) -> None:
    """`DELETE /authors/{id}` - stamps `deleted_at`; the row stays in the DB."""
    author = repo.get_by_id(db, author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Author with id {author_id} not found",
        )
    repo.soft_delete(db, author)
