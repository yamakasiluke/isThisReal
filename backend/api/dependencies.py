from __future__ import annotations

from backend.db.database import initialize_database
from backend.settings import Settings, get_settings


def settings_dependency() -> Settings:
    return get_settings()


def ensure_database_ready() -> None:
    initialize_database(get_settings())
