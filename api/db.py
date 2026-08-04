"""Database connections for the API.

Reuses the URL parser and dialect handling from tools/ls_db.py so the API and
the load scripts always speak the same dialect. lookup.py wants a raw DB-API
connection; use `db.connection` for that.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from api.config import get_database_url
from tools.ls_db import Database, connect


@contextmanager
def db_session(database_url: str | None = None) -> Iterator[Database]:
    """Open a connection, yield it, and always close it afterwards."""
    db = connect(database_url or get_database_url())
    try:
        yield db
    finally:
        db.close()
