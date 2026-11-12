# Import models here so `Base.metadata.create_all()` (and Alembic later)
# can see every table when the app starts.
from app.models.author import Author  # noqa: F401
