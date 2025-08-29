# Re-export Base from the application's DB layer to ensure a single metadata
from app.db.base import Base  # noqa: F401
