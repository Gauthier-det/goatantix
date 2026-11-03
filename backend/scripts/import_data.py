#!/usr/bin/env python3
"""Re-import all raw JSON files on disk into the DB (idempotent).

Useful after wiping the DB, or after changing the tokenizer, without
re-hitting the Genius API.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.importer import import_all  # noqa: E402


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        stats = import_all(db)
        print(f"Imported {stats.imported} new songs, skipped {stats.skipped} already present.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
