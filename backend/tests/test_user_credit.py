import unittest
from datetime import UTC, datetime, timedelta

from backend.core.schemas import UserReview, Verdict
from backend.core.user_credit import apply_credit_to_confidence, calculate_user_credit


class UserCreditTest(unittest.TestCase):
    def test_credit_increases_with_recent_validated_accuracy(self) -> None:
        now = datetime.now(UTC)
        reviews = [
            UserReview(
                user_id="reviewer-1",
                analysis_id="a1",
                verdict=Verdict.SUSPICIOUS,
                confidence=0.9,
                created_at=(now - timedelta(days=3)).isoformat(),
                validated_accuracy=True,
            ),
            UserReview(
                user_id="reviewer-1",
                analysis_id="a2",
                verdict=Verdict.UNCLEAR,
                confidence=0.8,
                created_at=(now - timedelta(days=8)).isoformat(),
                validated_accuracy=True,
            ),
        ]

        snapshot = calculate_user_credit("reviewer-1", reviews, now=now)

        self.assertGreater(snapshot.credibility_score, 0.7)

    def test_user_credit_only_bounded_confidence(self) -> None:
        review = UserReview(
            user_id="reviewer-1",
            analysis_id="a1",
            verdict=Verdict.SUSPICIOUS,
            confidence=1.0,
            validated_accuracy=True,
        )
        snapshot = calculate_user_credit("reviewer-1", [review])

        adjusted = apply_credit_to_confidence(
            0.55,
            Verdict.SUSPICIOUS,
            [review],
            {"reviewer-1": snapshot},
        )

        self.assertGreater(adjusted, 0.55)
        self.assertLessEqual(adjusted - 0.55, 0.15)


if __name__ == "__main__":
    unittest.main()
