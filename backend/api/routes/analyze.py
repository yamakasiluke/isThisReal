from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.analysis_pipeline import analyze_tweet
from backend.core.schemas import TweetInput, TweetMetadata, dataclass_to_dict
from backend.db.repository import get_analysis_payload, list_recent_analyses, save_analysis


router = APIRouter(tags=["analysis"])


class TweetMetadataRequest(BaseModel):
    tweet_id: str | None = None
    author_handle: str | None = None
    author_verified: bool | None = None
    author_account_age_days: int | None = None
    follower_count: int | None = None
    following_count: int | None = None
    retweet_count: int | None = None
    like_count: int | None = None
    quote_count: int | None = None
    has_media: bool | None = None
    created_at: str | None = None


class AnalyzeRequest(BaseModel):
    text: str | None = Field(default=None, max_length=4000)
    tweet_url: str | None = Field(default=None, max_length=500)
    source: str = Field(default="website", max_length=40)
    requester_id: str | None = Field(default=None, max_length=120)
    metadata: TweetMetadataRequest | None = None


@router.post("/analyze")
async def analyze(request: AnalyzeRequest) -> dict:
    if not request.text and not request.tweet_url:
        raise HTTPException(status_code=422, detail="Provide tweet text, a tweet URL, or both.")

    metadata = TweetMetadata(**request.metadata.model_dump()) if request.metadata else None
    result = await analyze_tweet(
        TweetInput(
            text=request.text,
            tweet_url=request.tweet_url,
            source=request.source,
            requester_id=request.requester_id,
            metadata=metadata,
        )
    )
    save_analysis(result)
    return dataclass_to_dict(result)


@router.get("/analyses")
async def analyses(limit: int = 25) -> list[dict]:
    return list_recent_analyses(limit=max(1, min(limit, 100)))


@router.get("/analyses/{analysis_id}")
async def analysis_detail(analysis_id: str) -> dict:
    payload = get_analysis_payload(analysis_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return payload
