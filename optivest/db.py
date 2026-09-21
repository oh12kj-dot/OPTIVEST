from __future__ import annotations
import os
import sqlite3
from datetime import date, datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

class Base(DeclarativeBase): pass

# Python 3.12 deprecated sqlite3's implicit date/datetime adapters. Register the
# exact ISO encodings SQLAlchemy's SQLite Date/DateTime types already expect.
sqlite3.register_adapter(date, lambda value: value.isoformat())
sqlite3.register_adapter(datetime, lambda value: value.isoformat(" "))

def database_url() -> str:
    return os.environ.get("OPTIVEST_DATABASE_URL", "sqlite:///./optivest.db")

def make_session(url: str | None = None):
    resolved = url or database_url()
    options = {"connect_args": {"check_same_thread": False}} if resolved.startswith("sqlite") else {}
    if resolved.endswith(":memory:"): options["poolclass"] = StaticPool
    engine = create_engine(resolved, future=True, **options)
    if resolved.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _foreign_keys(connection, _): connection.execute("PRAGMA foreign_keys=ON")
    return engine, sessionmaker(bind=engine, expire_on_commit=False)
