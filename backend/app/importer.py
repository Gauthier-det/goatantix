"""Imports raw JSON files collected from Genius into the Postgres database."""
import json
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.collector import slugify
from app.config import settings
from app.models import Artist, Song
from app.text_utils import clean_lyrics, distinct_word_tokens, tokenize


@dataclass
class ImportStats:
    imported: int
    skipped: int


def _get_or_create_artist(db: Session, name: str, genius_id: int) -> Artist:
    artist = db.query(Artist).filter(Artist.genius_id == genius_id).one_or_none()
    if artist:
        return artist
    artist = Artist(genius_id=genius_id, name=name, slug=slugify(name))
    db.add(artist)
    db.flush()
    return artist


def import_song_payload(db: Session, payload: dict) -> bool:
    """Returns True if a new Song row was created."""
    existing = db.query(Song).filter(Song.genius_id == payload["genius_id"]).one_or_none()
    if existing:
        return False

    artist = _get_or_create_artist(db, payload["artist_name"], payload["artist_genius_id"])

    lyrics = clean_lyrics(payload["lyrics"])
    tokens = tokenize(lyrics)
    title_tokens = distinct_word_tokens(payload["title"])

    song = Song(
        artist_id=artist.id,
        genius_id=payload["genius_id"],
        title=payload["title"],
        title_slug=slugify(payload["title"]),
        album=payload.get("album"),
        release_date=payload.get("release_date"),
        release_year=payload.get("release_year"),
        raw_lyrics=lyrics,
        tokens=tokens,
        title_tokens=title_tokens,
    )
    db.add(song)
    return True


def import_artist_dir(db: Session, artist_slug: str) -> ImportStats:
    artist_dir = settings.raw_dir / artist_slug
    if not artist_dir.exists():
        raise FileNotFoundError(f"No raw data for artist slug {artist_slug!r} in {settings.raw_dir}")

    imported = skipped = 0
    for json_file in sorted(artist_dir.glob("*.json")):
        payload = json.loads(json_file.read_text(encoding="utf-8"))
        if import_song_payload(db, payload):
            imported += 1
        else:
            skipped += 1
    db.commit()
    return ImportStats(imported=imported, skipped=skipped)


def import_all(db: Session) -> ImportStats:
    imported = skipped = 0
    for artist_dir in sorted(settings.raw_dir.iterdir()):
        if not artist_dir.is_dir():
            continue
        stats = import_artist_dir(db, artist_dir.name)
        imported += stats.imported
        skipped += stats.skipped
    return ImportStats(imported=imported, skipped=skipped)
