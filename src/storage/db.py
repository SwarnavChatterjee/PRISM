"""SQLite helpers for the local MVP knowledge store."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def init_db(db_path: str = "compliance.db") -> None:
    """Create the MVP tables if they do not already exist."""
    schema_path = Path(__file__).resolve().parents[2] / "database" / "schema.sql"
    with sqlite3.connect(db_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))


def connect(db_path: str = "compliance.db") -> sqlite3.Connection:
    init_db(db_path)
    return sqlite3.connect(db_path)
