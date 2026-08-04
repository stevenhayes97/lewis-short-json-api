"""Runtime settings for the API.

Kept deliberately small: one environment variable for the database, with a
SQLite default that matches the tools/README examples.
"""

from __future__ import annotations

import os

# Same URL shapes as tools/ls_db.py:
#   sqlite:///lewis_short.db
#   postgresql://user:password@localhost/lewis_short
DEFAULT_DATABASE_URL = "sqlite:///lewis_short.db"


def get_database_url() -> str:
    return os.environ.get("LEWIS_SHORT_DATABASE_URL", DEFAULT_DATABASE_URL)
