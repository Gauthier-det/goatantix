#!/usr/bin/env python3
"""(Re)trains the Word2Vec model used to score guesses, from everything currently in the DB.

Run this after every collection batch (or at least before the first game).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal  # noqa: E402
from app.embeddings import train_and_save  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        vocab_size = train_and_save(db)
        print(f"Trained Word2Vec model, vocabulary size: {vocab_size}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
