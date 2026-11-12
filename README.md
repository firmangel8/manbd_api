# Library API — FastAPI Starter Kit

A minimal, well-structured FastAPI project demonstrating **full CRUD** on the
`authors` resource, backed by the MySQL database `db_library`.
Built as a starter kit for students learning to build RESTful APIs.

## Project Structure (Blueprint Architecture)

FastAPI's equivalent of "blueprints" is **modular `APIRouter`s**. Each resource
is self-contained, and the layers have one job each:

```
app/
├── main.py                    # App entry point: creates FastAPI, mounts routers
├── core/
│   ├── config.py              # Settings loaded from .env (no hard-coded secrets)
│   └── database.py            # Engine + session factory + get_db dependency
├── models/                    # SQLAlchemy models  → how data is STORED
│   └── author.py              #   maps to table tb_authors
├── schemas/                   # Pydantic schemas   → how data is SHIPPED
│   └── author.py              #   request/response JSON shapes + validation
├── repositories/              # Data access layer  → all SQL/CRUD logic
│   └── author_repository.py
└── api/
    ├── deps.py                # Shared dependencies (get_db, auth later...)
    └── v1/
        ├── router.py          # v1 "blueprint": registers all v1 resources
        └── endpoints/
            └── authors.py     # HTTP endpoints only (no SQL here!)
```

**Request flow:**

```
HTTP request → endpoint (authors.py) → repository → SQLAlchemy model → MySQL
             ← JSON (schema)         ←             ←                 ←
```

**To add a new resource (e.g. books):** create `models/book.py`,
`schemas/book.py`, `repositories/book_repository.py`,
`api/v1/endpoints/books.py`, then one line in `api/v1/router.py`. Done.

## Requirements

- Python 3.11+
- MySQL running locally with the `db_library` database
  (import `db_library_withdata.sql` if you don't have it yet:
  `mysql -u root -p < db_library_withdata.sql`)

## Setup

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your database connection
cp .env.example .env               # then edit .env with your MySQL user/password
```

## Run

```bash
uvicorn app.main:app --reload
```

- Interactive API docs (Swagger UI): **http://localhost:8000/docs**
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## API Endpoints

| Method | URL                        | Description                                  |
|--------|----------------------------|----------------------------------------------|
| GET    | `/api/v1/authors`          | List authors (query: `?search=&skip=&limit=`)|
| GET    | `/api/v1/authors/{id}`     | Get one author                               |
| POST   | `/api/v1/authors`          | Create an author                             |
| PUT    | `/api/v1/authors/{id}`     | Update an author                             |
| DELETE | `/api/v1/authors/{id}`     | Soft-delete an author (sets `deleted_at`)    |

### Try it with curl

```bash
# List
curl http://localhost:8000/api/v1/authors

# Search
curl "http://localhost:8000/api/v1/authors?search=Orwell&limit=5"

# Create
curl -X POST http://localhost:8000/api/v1/authors \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Aldous", "last_name": "Huxley"}'

# Update
curl -X PUT http://localhost:8000/api/v1/authors/1 \
  -H "Content-Type: application/json" \
  -d '{"first_name": "George", "last_name": "Orwell (updated)"}'

# Delete (soft delete - row stays, deleted_at is set)
curl -X DELETE http://localhost:8000/api/v1/authors/1
```

## Concepts Demonstrated

- **Blueprint-style routing** — versioned `APIRouter`s (`/api/v1/...`)
- **Layered architecture** — endpoints / repositories / models / schemas
- **Dependency Injection** — `Depends(get_db)` provides a per-request DB session
- **ORM** — SQLAlchemy 2.0 `Mapped`/`mapped_column` mapped to the real schema
- **Validation** — Pydantic v2 schemas with field constraints
- **Soft delete** — `deleted_at` timestamp instead of destroying rows
- **Configuration** — environment variables via `pydantic-settings` (`.env`)
- **Auto docs** — Swagger UI generated from type hints at `/docs`
