#!/usr/bin/env python3
"""One-off migration: adds the songs.active column (defaulting to true) to an existing DB.

`Base.metadata.create_all` (run on API startup) only creates missing tables, it never
alters an existing one, so this has to be run once by hand after pulling the `active`
column onto the Song model.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.db import engine  # noqa: E402


def main() -> None:
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE songs ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE")
        )
    print("songs.active column present.")


if __name__ == "__main__":
    main()
