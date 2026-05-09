from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./data/isthisreal.db"
    llm_provider: str = "heuristic"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    openai_api_key: str | None = None
    website_base_url: str = "http://localhost:3000"
    cors_origins: tuple[str, ...] = ("http://localhost:3000",)
    x_api_bearer_token: str | None = None


def _split_origins(value: str | None) -> tuple[str, ...]:
    if not value:
        return ("http://localhost:3000",)
    return tuple(origin.strip() for origin in value.split(",") if origin.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/isthisreal.db"),
        llm_provider=os.getenv("LLM_PROVIDER", "heuristic").strip().lower(),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        website_base_url=os.getenv("WEBSITE_BASE_URL", "http://localhost:3000"),
        cors_origins=_split_origins(os.getenv("BACKEND_CORS_ORIGINS")),
        x_api_bearer_token=os.getenv("X_API_BEARER_TOKEN") or None,
    )
