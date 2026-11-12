# Architecture Diagrams (Mermaid)

Render these at https://mermaid.js.org or any Mermaid viewer.
Two diagrams: (1) layered architecture / request flow, (2) data model.

## 1. Layered Architecture / Request Flow

```mermaid
flowchart TB
    Client["🧑‍🎓 Student / Client<br/>(curl · Postman · /docs)"]

    subgraph HTTP["HTTP Layer"]
        MAIN["app/main.py<br/>FastAPI app<br/>lifespan: create tables + SELECT 1"]
        ROUTER["app/api/v1/router.py<br/>api_router  •  prefix /api/v1"]
        EP["app/api/v1/endpoints/authors.py<br/>GET '' · GET /{id} · POST · PUT /{id} · DELETE /{id}"]
    end

    subgraph LOGIC["Business Logic Layer"]
        REPO["app/repositories/author_repository.py<br/>get_all · get_by_id · create · update · soft_delete<br/>(soft delete → deleted_at IS NULL)"]
    end

    subgraph DATA["Data Layer"]
        MODEL["app/models/author.py<br/>Author (SQLAlchemy ORM)<br/>maps → tb_authors"]
        DB[("🗄️ MySQL<br/>db_library<br/>tb_authors")]
    end

    subgraph CROSS["Cross-cutting (Dependency Injection)"]
        SCHEMA["app/schemas/author.py<br/>AuthorCreate · AuthorUpdate<br/>AuthorResponse · AuthorListResponse"]
        DEPS["app/api/deps.py<br/>get_db → one Session per request"]
        CONFIG["app/core/config.py<br/>Settings from .env"]
        CORE["app/core/database.py<br/>Base · engine · SessionLocal"]
    end

    Client -->|"GET /api/v1/authors..."| MAIN
    MAIN --> ROUTER --> EP
    EP -->|"1. validates body with<br/>Pydantic schemas"| SCHEMA
    EP -->|"2. Depends(get_db)"| DEPS
    EP -->|"3. calls CRUD functions"| REPO
    REPO -->|"ORM queries"| MODEL
    MODEL -->|"SQL (pymysql)"| DB
    DEPS --> CORE
    CORE -->|"builds connection URL"| CONFIG
    CORE --> DB

    style HTTP fill:#e8f4fd,stroke:#2196f3
    style LOGIC fill:#fff8e1,stroke:#ffc107
    style DATA fill:#e8f5e9,stroke:#4caf50
    style CROSS fill:#f3e5f5,stroke:#9c27b0
```

## 2. Data Model (tb_authors)

```mermaid
erDiagram
    TB_AUTHORS {
        int author_id PK "AUTO_INCREMENT"
        varchar_50 first_name "NOT NULL"
        varchar_50 last_name "NOT NULL"
        timestamp created_at "DEFAULT now()"
        timestamp updated_at "DEFAULT now()"
        timestamp deleted_at "NULL = alive (soft delete)"
    }
    TB_BOOKS {
        int book_id PK
        varchar_100 title
        int author_id FK "nullable"
        int publication_year
        varchar_50 genre
    }
    TB_BOOKS }o--o| TB_AUTHORS : "author_id"
```

## How to read diagram 1 (the one to present)

A request enters through `main.py` → the v1 router (the "blueprint") → the
`authors` endpoint. The endpoint does three things: validates JSON with
**schemas**, borrows a DB session via **`Depends(get_db)`**, and delegates the
real work to the **repository**, which uses the SQLAlchemy **model** to talk to
MySQL. The purple box is cross-cutting — shared by every resource, so when
students add a new resource (e.g. `books`), they only create a new endpoint +
repository + model and register one line in `router.py`.

## Why DELETE is a soft delete (diagram 2)

`deleted_at` stays `NULL` for alive rows, and every read in the repository
filters `deleted_at IS NULL` — matching the real `db_library` schema.
