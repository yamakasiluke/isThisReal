from __future__ import annotations

import math
from datetime import UTC, datetime

from backend.core.schemas import UserCreditSnapshot, UserReview, Verdict, clamp, utc_now_iso


INITIAL_CREDIT = 0.5
MIN_CREDIT = 0.2
MAX_CREDIT = 0.9
MAX_CONFIDENCE_SWING = 0.15


def calculate_user_credit(user_id: str, reviews: list[UserReview], now: datetime | None = None) -> UserCreditSnapshot:
    now = now or datetime.now(UTC)
    validated = [review for review in reviews if review.validated_accuracy is not None]
    if not validated:
        return UserCreditSnapshot(user_id=user_id, credibility_score=INITIAL_CREDIT)

    weighted_total = 0.0
    weighted_correct = 0.0
    for review in validated:
        age_days = _age_days(review.created_at, now)
        recency_weight = math.exp(-0.02 * age_days)
        confidence_weight = clamp(review.confidence, 0.2, 1.0)
        weight = recency_weight * confidence_weight
        weighted_total += weight
        if review.validated_accuracy:
            weighted_correct += weight

    accuracy = weighted_correct / max(weighted_total, 0.0001)
    score = clamp((INITIAL_CREDIT * 0.35) + (accuracy * 0.65), MIN_CREDIT, MAX_CREDIT)
    return UserCreditSnapshot(
        user_id=user_id,
        credibility_score=round(score, 3),
        reviews_count=len(validated),
        correct_count=sum(1 for review in validated if review.validated_accuracy),
        last_updated=utc_now_iso(),
        reason="recency_weighted_validation",
    )


def apply_credit_to_confidence(
    base_confidence: float,
    automated_verdict: Verdict,
    reviews: list[UserReview],
    credit_snapshots: dict[str, UserCreditSnapshot],
) -> float:
    if not reviews or base_confidence >= 0.72:
        return base_confidence

    total_weight = 0.0
    agreement_weight = 0.0
    for review in reviews:
        credit = credit_snapshots.get(review.user_id)
        if not credit:
            continue
        bounded_credit = clamp(credit.credibility_score, MIN_CREDIT, MAX_CREDIT)
        weight = bounded_credit * clamp(review.confidence, 0.2, 1.0)
        total_weight += weight
        if review.verdict == automated_verdict:
            agreement_weight += weight
        else:
            agreement_weight -= weight

    if total_weight <= 0:
        return base_confidence

    agreement_ratio = agreement_weight / total_weight
    adjustment = agreement_ratio * MAX_CONFIDENCE_SWING
    return round(clamp(base_confidence + adjustment, 0.2, 0.9), 3)


def _age_days(created_at: str, now: datetime) -> float:
    try:
        parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return 90.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return max((now - parsed).total_seconds() / 86400, 0.0)
