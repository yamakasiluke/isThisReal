from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class Verdict(str, Enum):
    LIKELY_TRUE = "likely_true"
    SUSPICIOUS = "suspicious"
    UNCLEAR = "unclear"


class ClaimType(str, Enum):
    FACTUAL = "factual"
    TEMPORAL = "temporal"
    STATISTICAL = "statistical"
    ATTRIBUTED = "attributed"
    OPINION = "opinion"


@dataclass(slots=True)
class TweetInput:
    text: str | None = None
    tweet_url: str | None = None
    source: str = "website"
    requester_id: str | None = None
    metadata: "TweetMetadata | None" = None


@dataclass(slots=True)
class TweetMetadata:
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


@dataclass(slots=True)
class ExtractedClaim:
    text: str
    claim_type: ClaimType = ClaimType.FACTUAL
    confidence: float = 0.5


@dataclass(slots=True)
class Signal:
    name: str
    value: bool | int | float | str | None
    weight: float
    priority: str = "medium"
    description: str = ""


@dataclass(slots=True)
class RuleDecision:
    rule_id: str
    name: str
    triggered: bool
    score_delta: float
    verdict_hint: Verdict
    confidence_boost: float
    reason: str


@dataclass(slots=True)
class LLMJudgment:
    verdict: Verdict
    confidence: float
    reasoning: str
    caveats: list[str] = field(default_factory=list)
    model_name: str = "heuristic-offline"


@dataclass(slots=True)
class UserReview:
    user_id: str
    analysis_id: str
    verdict: Verdict
    confidence: float = 0.5
    created_at: str = field(default_factory=utc_now_iso)
    validation_status: str = "pending"
    validated_accuracy: bool | None = None


@dataclass(slots=True)
class UserCreditSnapshot:
    user_id: str
    credibility_score: float = 0.5
    reviews_count: int = 0
    correct_count: int = 0
    last_updated: str = field(default_factory=utc_now_iso)
    reason: str = "neutral_start"


@dataclass(slots=True)
class AnalysisResult:
    analysis_id: str
    input: TweetInput
    tweet_id: str | None
    verdict: Verdict
    confidence: float
    reasoning: str
    claims: list[ExtractedClaim]
    signals: list[Signal]
    rule_decisions: list[RuleDecision]
    llm_judgment: LLMJudgment
    suspicion_score: float
    prompt_version: str = "tweet_judge_v1"
    ruleset_version: str = "rules_v1"
    model_name: str = "heuristic-offline"
    disclaimer: str = (
        "This is a credibility signal, not an authoritative fact-check. "
        "Review the original source and evidence before acting on it."
    )
    created_at: str = field(default_factory=utc_now_iso)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def dataclass_to_dict(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: dataclass_to_dict(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [dataclass_to_dict(item) for item in value]
    if isinstance(value, tuple):
        return tuple(dataclass_to_dict(item) for item in value)
    if isinstance(value, dict):
        return {key: dataclass_to_dict(item) for key, item in value.items()}
    return value
