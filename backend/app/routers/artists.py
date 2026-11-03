from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import collector, importer
from app.auth import require_admin
from app.db import get_db
from app.models import Artist, Song
from app.schemas import ArtistOut, CollectRequest, CollectResult

router = APIRouter(prefix="/api/artists", tags=["artists"])


@router.get("", response_model=list[ArtistOut])
def list_artists(db: Session = Depends(get_db)):
    rows = (
        db.query(Artist, func.count(Song.id))
        .outerjoin(Song, Song.artist_id == Artist.id)
        .group_by(Artist.id)
        .order_by(Artist.name)
        .all()
    )
    return [ArtistOut(id=a.id, name=a.name, slug=a.slug, song_count=count) for a, count in rows]


@router.post("/collect", response_model=CollectResult, dependencies=[Depends(require_admin)])
def collect_artist(req: CollectRequest, db: Session = Depends(get_db)):
    """Fetches an artist's songs from Genius, saves raw JSON, then imports into DB.

    This can take a while for artists with a large catalog (Genius scraping is slow).
    """
    try:
        stats = collector.collect_artist(req.name, max_songs=req.max_songs)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    artist_slug = collector.slugify(stats.artist)
    import_stats = importer.import_artist_dir(db, artist_slug)

    return CollectResult(
        artist=stats.artist,
        songs_collected=stats.songs_collected,
        songs_imported=import_stats.imported,
    )
