from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.core.schemas import Verdict, clamp
from backend.db.repository import add_review


router = APIRouter(tags=["reviews"])


class ReviewRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=120)
    analysis_id: str = Field(min_length=1, max_length=120)
    verdict: Verdict
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    comment: str | None = Field(default=None, max_length=1200)


@router.post("/reviews")
async def review(request: ReviewRequest) -> dict:
    return add_review(
        user_id=request.user_id,
        analysis_id=request.analysis_id,
        verdict=request.verdict,
        confidence=clamp(request.confidence),
        comment=request.comment,
    )
