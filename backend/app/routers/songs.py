from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.auth import require_admin
from app.db import get_db
from app.models import Artist, Song
from app.schemas import SongOut, SongUpdateRequest

router = APIRouter(prefix="/api/songs", tags=["songs"], dependencies=[Depends(require_admin)])


def _to_out(song: Song) -> SongOut:
    return SongOut(
        id=song.id,
        title=song.title,
        artist_name=song.artist.name,
        release_year=song.release_year,
        active=song.active,
    )


@router.get("", response_model=list[SongOut])
def list_songs(search: str = "", db: Session = Depends(get_db)):
    query = db.query(Song).join(Artist).options(joinedload(Song.artist))
    if search.strip():
        like = f"%{search.strip()}%"
        query = query.filter(or_(Song.title.ilike(like), Artist.name.ilike(like)))
    songs = query.order_by(Artist.name, Song.title).all()
    return [_to_out(s) for s in songs]


@router.patch("/{song_id}", response_model=SongOut)
def update_song(song_id: int, req: SongUpdateRequest, db: Session = Depends(get_db)):
    song = db.get(Song, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    song.active = req.active
    db.commit()
    db.refresh(song)
    return _to_out(song)
