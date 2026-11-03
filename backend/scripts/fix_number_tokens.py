#!/usr/bin/env python3
"""Recomputes tokens/title_tokens for songs already in the DB after the tokenizer fix.

Digit runs ("2024", "100", ...) used to be classified as non-word tokens, so they were
always shown unmasked and could never be guessed. Now that tokenize() treats them as
words, this re-derives tokens/title_tokens from each song's stored raw_lyrics/title.
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
            new_tokens = tokenize(song.raw_lyrics)
            new_title_tokens = list(
                dict.fromkeys(
                    normalize_word(t["t"]) for t in tokenize(song.title) if t["w"] and normalize_word(t["t"])
                )
            )
            if new_tokens != song.tokens or new_title_tokens != song.title_tokens:
                song.tokens = new_tokens
                song.title_tokens = new_title_tokens
                fixed += 1
        db.commit()
        print(f"Checked {len(songs)} songs, fixed {fixed} with stale tokens.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
