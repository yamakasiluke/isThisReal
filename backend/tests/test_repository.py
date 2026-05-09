from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from backend.core.analysis_pipeline import analyze_tweet
from backend.core.schemas import TweetInput, Verdict
from backend.db.database import connect
from backend.db.repository import add_review, get_analysis_payload, list_recent_analyses, save_analysis
from backend.settings import Settings


class RepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.settings = Settings(database_url=f"sqlite:///{Path(self.temp_dir.name) / 'repository-test.db'}")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_save_analysis_round_trip_and_audit(self) -> None:
        result = asyncio.run(
            analyze_tweet(
                TweetInput(
                    text="BREAKING people are saying 88 percent disappeared, share before they delete this.",
                    source="repository-test",
                )
            )
        )

        save_analysis(result, self.settings)
        recent = list_recent_analyses(limit=1, settings=self.settings)
        payload = get_analysis_payload(result.analysis_id, self.settings)

        self.assertEqual(recent[0]["analysis_id"], result.analysis_id)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["analysis_id"], result.analysis_id)

        with connect(self.settings) as connection:
            audit_count = connection.execute(
                "SELECT COUNT(*) AS count FROM audit_events WHERE analysis_id = ?",
                (result.analysis_id,),
            ).fetchone()["count"]
        self.assertEqual(audit_count, 1)

    def test_add_review_records_review_and_audit_event(self) -> None:
        result = asyncio.run(analyze_tweet(TweetInput(text="People are saying the event happened.")))
        save_analysis(result, self.settings)

        review = add_review(
            user_id="reviewer-1",
            analysis_id=result.analysis_id,
            verdict=Verdict.UNCLEAR,
            confidence=0.55,
            comment="Needs more context.",
            settings=self.settings,
        )

        self.assertEqual(review["verdict"], "unclear")
        with connect(self.settings) as connection:
            review_count = connection.execute("SELECT COUNT(*) AS count FROM user_reviews").fetchone()["count"]
            audit_count = connection.execute(
                "SELECT COUNT(*) AS count FROM audit_events WHERE event_type = 'review_added'"
            ).fetchone()["count"]
        self.assertEqual(review_count, 1)
        self.assertEqual(audit_count, 1)


if __name__ == "__main__":
    unittest.main()
