from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import game as game_logic
from app.db import get_db
from app.models import Game, Song
from app.schemas import GameStateOut, GuessRequest, NewGameRequest

router = APIRouter(prefix="/api/game", tags=["game"])


def _get_game_and_song(db: Session, game_id: int) -> tuple[Game, Song]:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    song = db.get(Song, game.song_id)
    return game, song


@router.post("/new", response_model=GameStateOut)
def new_game(req: NewGameRequest, db: Session = Depends(get_db)):
    try:
        if req.mode == "daily":
            song = game_logic.pick_daily_song(db)
        else:
            song = game_logic.pick_song(db, req.artist_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    game = Game(song_id=song.id, guesses=[], mode=req.mode)
    db.add(game)
    db.commit()
    db.refresh(game)

    return game_logic.build_state(game, song)


@router.get("/{game_id}", response_model=GameStateOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game, song = _get_game_and_song(db, game_id)
    return game_logic.build_state(game, song)


@router.post("/{game_id}/guess", response_model=GameStateOut)
def guess(game_id: int, req: GuessRequest, db: Session = Depends(get_db)):
    game, song = _get_game_and_song(db, game_id)
    try:
        return game_logic.process_guess(db, game, song, req.word)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
