import random
from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import embeddings
from app.models import DailyChallenge, Game, Song
from app.schemas import GameStateOut, GuessResultOut, TokenOut
from app.text_utils import distinct_word_tokens, normalize_word


def pick_song(db: Session, artist_id: int | None) -> Song:
    query = db.query(Song).filter(Song.active.is_(True))
    if artist_id is not None:
        query = query.filter(Song.artist_id == artist_id)
    songs = query.all()
    if not songs:
        raise ValueError("No active songs available for that selection — enable some songs first.")
    return random.choice(songs)


def pick_daily_song(db: Session) -> Song:
    """Pins one song per calendar day (server local time), reused by everyone until midnight."""
    today = date.today()
    challenge = db.query(DailyChallenge).filter(DailyChallenge.challenge_date == today).one_or_none()
    if challenge is None:
        songs = db.query(Song).filter(Song.active.is_(True)).all()
        if not songs:
            raise ValueError("No active songs available — enable some songs first.")
        used_ids = {row[0] for row in db.query(DailyChallenge.song_id).all()}
        candidates = [s for s in songs if s.id not in used_ids] or songs
        song = random.choice(candidates)
        challenge = DailyChallenge(challenge_date=today, song_id=song.id)
        db.add(challenge)
        try:
            db.commit()
        except IntegrityError:
            # Another request picked today's song in the meantime.
            db.rollback()
            challenge = db.query(DailyChallenge).filter(DailyChallenge.challenge_date == today).one()
    return db.get(Song, challenge.song_id)


def _found_words(game: Game) -> set[str]:
    return {
        g["norm"] for g in game.guesses if g["count"] > 0 or g["in_title"] or g.get("in_artist")
    }


def _mask_tokens(tokens: list[dict], found: set[str]) -> list[TokenOut]:
    out = []
    for tok in tokens:
        if not tok["w"]:
            out.append(TokenOut(t=tok["t"], w=False, revealed=True))
            continue
        norm = normalize_word(tok["t"])
        revealed = norm in found or norm == ""
        out.append(TokenOut(t=tok["t"] if revealed else "•" * len(tok["t"]), w=True, revealed=revealed))
    return out


def _mask_word_list(tokens: list[str], found: set[str]) -> list[TokenOut]:
    out = []
    for norm in tokens:
        revealed = norm in found
        out.append(TokenOut(t=norm if revealed else "•" * len(norm), w=True, revealed=revealed))
    return out


def _is_fully_found(tokens: list[str], found: set[str]) -> bool:
    return all(t in found for t in tokens) if tokens else True


# Finding the artist plus this share of the lyrics words also counts as a win,
# even if the exact title was never guessed.
LYRICS_WIN_COVERAGE = 0.3


def _lyrics_coverage(tokens: list[dict], found: set[str]) -> float:
    word_tokens = [t for t in tokens if t["w"]]
    if not word_tokens:
        return 1.0
    revealed = sum(1 for t in word_tokens if normalize_word(t["t"]) in found)
    return revealed / len(word_tokens)


def _is_won(song: Song, found: set[str], artist_found: bool) -> bool:
    if _is_fully_found(song.title_tokens, found):
        return True
    return artist_found and _lyrics_coverage(song.tokens, found) >= LYRICS_WIN_COVERAGE


def build_state(game: Game, song: Song) -> GameStateOut:
    found = _found_words(game)
    artist_tokens = distinct_word_tokens(song.artist.name)
    artist_found = _is_fully_found(artist_tokens, found)
    is_found = _is_won(song, found, artist_found)
    return GameStateOut(
        game_id=game.id,
        mode=game.mode,
        release_year=song.release_year,
        tokens=_mask_tokens(song.tokens, found),
        title_tokens=_mask_word_list(song.title_tokens, found),
        found=is_found,
        artist_tokens=_mask_word_list(artist_tokens, found),
        artist_found=artist_found,
        # chronological (oldest first); the frontend shows most-recent-first
        guesses=[GuessResultOut(**g) for g in game.guesses],
        title=song.title if is_found else None,
        full_lyrics=song.raw_lyrics if is_found else None,
        artist_name=song.artist.name if artist_found else None,
    )


def process_guess(db: Session, game: Game, song: Song, raw_word: str) -> GameStateOut:
    norm = normalize_word(raw_word)
    if not norm:
        raise ValueError("Empty guess")

    existing = next((g for g in game.guesses if g["norm"] == norm), None)
    if existing is None:
        count = sum(1 for t in song.tokens if t["w"] and normalize_word(t["t"]) == norm)
        in_title = norm in song.title_tokens
        in_artist = norm in distinct_word_tokens(song.artist.name)
        if count > 0 or in_title or in_artist:
            score, rank = 1.0, 1
        else:
            try:
                score, rank = embeddings.score_guess(norm, song.title_tokens)
            except RuntimeError:
                # No embeddings trained yet: exact matches still work, just no proximity hint.
                score, rank = 0.0, None

        entry = {
            "word": raw_word,
            "norm": norm,
            "score": score,
            "rank": rank,
            "count": count,
            "in_title": in_title,
            "in_artist": in_artist,
        }
        game.guesses = [*game.guesses, entry]
        db.add(game)

    found = _found_words(game)
    artist_tokens = distinct_word_tokens(song.artist.name)
    game.found = _is_won(song, found, _is_fully_found(artist_tokens, found))
    db.commit()
    db.refresh(game)

    state = build_state(game, song)
    if existing is not None:
        # surface that this particular guess was a repeat, without duplicating it in the list
        for g in state.guesses:
            if g.norm == norm:
                g.already_guessed = True
    return state
