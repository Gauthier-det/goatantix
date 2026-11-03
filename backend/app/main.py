from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routers import artists, auth, game, songs

app = FastAPI(title="Goatantix API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(artists.router)
app.include_router(game.router)
app.include_router(songs.router)
app.include_router(auth.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
