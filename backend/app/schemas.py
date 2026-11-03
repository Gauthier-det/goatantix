from pydantic import BaseModel


class ArtistOut(BaseModel):
    id: int
    name: str
    slug: str
    song_count: int


class CollectRequest(BaseModel):
    name: str
    max_songs: int = 50


class CollectResult(BaseModel):
    artist: str
    songs_collected: int
    songs_imported: int


class NewGameRequest(BaseModel):
    artist_id: int | None = None
    mode: str = "random"  # "random" | "daily"


class SongOut(BaseModel):
    id: int
    title: str
    artist_name: str
    release_year: int | None
    active: bool


class SongUpdateRequest(BaseModel):
    active: bool


class AuthRequest(BaseModel):
    password: str


class AuthResult(BaseModel):
    ok: bool


class TokenOut(BaseModel):
    t: str
    w: bool
    revealed: bool


class GuessRequest(BaseModel):
    word: str


class GuessResultOut(BaseModel):
    word: str
    norm: str
    score: float
    rank: int | None
    count: int
    in_title: bool
    in_artist: bool = False
    already_guessed: bool = False


class GameStateOut(BaseModel):
    game_id: int
    mode: str
    release_year: int | None
    tokens: list[TokenOut]
    title_tokens: list[TokenOut]
    found: bool
    artist_tokens: list[TokenOut]
    artist_found: bool
    guesses: list[GuessResultOut]
    # only populated once found/artist_found
    title: str | None = None
    full_lyrics: str | None = None
    artist_name: str | None = None
