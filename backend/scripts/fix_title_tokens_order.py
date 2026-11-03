#!/usr/bin/env python3
"""Recomputes title_tokens in the original word order for songs already in the DB.

A past bug stored title_tokens alphabetically-sorted instead of in title order
(e.g. "Tout s'éteint" became [s'eteint, tout] instead of [tout, s'eteint]).
This re-derives title_tokens from each song's title using today's logic.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal  # noqa: E402
from app.models import Song  # noqa: E402
from app.text_utils import normalize_word, tokenize  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        songs = db.query(Song).all()
        fixed = 0
        for song in songs:
            correct = list(
                dict.fromkeys(
                    normalize_word(t["t"]) for t in tokenize(song.title) if t["w"] and normalize_word(t["t"])
                )
            )
            if correct != song.title_tokens:
                song.title_tokens = correct
                fixed += 1
        db.commit()
        print(f"Checked {len(songs)} songs, fixed {fixed} with wrong title_tokens order.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
