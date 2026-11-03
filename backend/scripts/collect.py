#!/usr/bin/env python3
"""Collect an artist's songs from Genius and import them into the DB.

Usage:
    python scripts/collect.py "Nekfeu" --max-songs 60
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import collector, importer  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artist", help="Artist name as it appears on Genius")
    parser.add_argument("--max-songs", type=int, default=50)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    print(f"Collecting songs for {args.artist!r} from Genius (max {args.max_songs})...")
    stats = collector.collect_artist(args.artist, max_songs=args.max_songs)
    print(f"Collected {stats.songs_collected} songs for {stats.artist}.")

    db = SessionLocal()
    try:
        artist_slug = collector.slugify(stats.artist)
        import_stats = importer.import_artist_dir(db, artist_slug)
        print(f"Imported {import_stats.imported} new songs ({import_stats.skipped} already in DB).")
    finally:
        db.close()

    print("Done. Run scripts/train_embeddings.py to (re)build the word vectors.")


if __name__ == "__main__":
    main()
