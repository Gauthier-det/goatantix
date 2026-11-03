"""Collects an artist's songs from Genius and dumps them as raw JSON files.

This step is deliberately separated from DB import: the raw JSON on disk is
the source of truth you can re-import at any time (e.g. after wiping the DB
or changing the tokenizer) without re-hitting the Genius API.
"""
import json
import re
from dataclasses import dataclass

import lyricsgenius
from unidecode import unidecode

from app.config import settings


def slugify(text: str) -> str:
    text = unidecode(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "unknown"


@dataclass
class CollectStats:
    artist: str
    songs_collected: int


def get_client() -> lyricsgenius.Genius:
    if not settings.genius_access_token:
        raise RuntimeError(
            "GENIUS_ACCESS_TOKEN is not set. Create a client at "
            "https://genius.com/api-clients and put the token in backend/.env"
        )
    genius = lyricsgenius.Genius(
        settings.genius_access_token,
        timeout=15,
        retries=3,
        skip_non_songs=True,
        remove_section_headers=False,
        excluded_terms=["(Remix)", "(Live)", "(Freestyle Radio)"],
        verbose=True,
    )
    return genius


def collect_artist(artist_name: str, max_songs: int = 50) -> CollectStats:
    genius = get_client()
    artist = genius.search_artist(artist_name, max_songs=max_songs, sort="popularity")
    if artist is None:
        raise ValueError(f"Artist not found on Genius: {artist_name!r}")

    artist_slug = slugify(artist.name)
    out_dir = settings.raw_dir / artist_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for song in artist.songs:
        if not song.lyrics:
            continue
        release_components = song._body.get("release_date_components") or {}
        payload = {
            "genius_id": song.id,
            "artist_name": artist.name,
            "artist_genius_id": artist.id,
            "title": song.title,
            "lyrics": song.lyrics,
            "album": song.album.name if song.album else None,
            "release_date": song._body.get("release_date_for_display"),
            "release_year": release_components.get("year"),
        }
        out_path = out_dir / f"{song.id}.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1

    return CollectStats(artist=artist.name, songs_collected=count)
