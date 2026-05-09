from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.dependencies import ensure_database_ready
from backend.api.routes import analyze, reviews
from backend.settings import get_settings


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_database_ready()
    yield

app = FastAPI(
    title="Is This Real API",
    description="Shared tweet credibility analysis API for the website and X/Twitter bot.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(reviews.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
