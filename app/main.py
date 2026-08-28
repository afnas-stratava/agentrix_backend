from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.voice import router as voice_router
from app.db.database import Base, engine
from app.models import user  # noqa: F401 — registers User with Base.metadata


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