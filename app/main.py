import logging

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.voice import router as voice_router
from app.db.database import Base, engine
from app.models import user  # noqa: F401 — registers User with Base.metadata

# Root logger defaults to WARNING, which would silently drop the app's own
# logger.info(...) calls (e.g. the per-phase timing breakdown in voice.py) —
# without this they'd never reach the console at all, not even show up as
# suppressed.
logging.basicConfig(level=logging.INFO, format="%(message)s")


app = FastAPI(
    title="Agentrix API",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(voice_router)


@app.get("/")
def root():
    return {
        "message": "Agentrix API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }