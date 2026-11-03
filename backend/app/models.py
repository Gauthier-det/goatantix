from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    genius_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    songs: Mapped[list["Song"]] = relationship(back_populates="artist", cascade="all, delete-orphan")


class Song(Base):
    __tablename__ = "songs"
    __table_args__ = (UniqueConstraint("genius_id", name="uq_song_genius_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), index=True)
    genius_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(500))
    title_slug: Mapped[str] = mapped_column(String(500))
    album: Mapped[str | None] = mapped_column(String(500), nullable=True)
    release_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_lyrics: Mapped[str] = mapped_column(Text)
    # tokens: list of {"t": text, "w": is_word(bool)} preserving original layout
    tokens: Mapped[list] = mapped_column(JSON)
    # title_tokens: list of normalized word tokens from the title (used as the guessing target)
    title_tokens: Mapped[list] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    artist: Mapped[Artist] = relationship(back_populates="songs")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), index=True)
    mode: Mapped[str] = mapped_column(String(20), default="random", server_default="random")
    found: Mapped[bool] = mapped_column(Boolean, default=False)
    # list of {"word", "norm", "score", "rank", "count", "in_title", "in_artist"}
    guesses: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    song: Mapped[Song] = relationship()


class DailyChallenge(Base):
    """Pins one song per calendar day for the 'Musique du jour' mode; resets at midnight."""

    __tablename__ = "daily_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"))

    song: Mapped[Song] = relationship()
