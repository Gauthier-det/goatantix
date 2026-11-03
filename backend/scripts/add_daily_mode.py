#!/usr/bin/env python3
"""One-off migration: adds games.mode and the daily_challenges table for 'Musique du jour'.

`Base.metadata.create_all` (run on API startup) only creates missing tables, it never
alters an existing one — the games.mode column has to be added by hand.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.models import DailyChallenge  # noqa: E402,F401  (registers the table on Base.metadata)


def main() -> None:
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE games ADD COLUMN IF NOT EXISTS mode VARCHAR(20) NOT NULL DEFAULT 'random'")
        )
    Base.metadata.create_all(bind=engine)
    print("games.mode column present, daily_challenges table present.")


if __name__ == "__main__":
    main()
