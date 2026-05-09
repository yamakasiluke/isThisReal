import asyncio
import unittest

from backend.core.analysis_pipeline import analyze_tweet
from backend.core.schemas import TweetInput, Verdict


class AnalysisPipelineTest(unittest.TestCase):
    def test_suspicious_language_returns_suspicious_signal(self) -> None:
        result = asyncio.run(
            analyze_tweet(
                TweetInput(
                    text="BREAKING: people are saying 90 percent of votes vanished. Share before they delete it.",
                )
            )
        )

        self.assertEqual(result.verdict, Verdict.SUSPICIOUS)
        self.assertGreater(result.confidence, 0.55)
        self.assertTrue(result.claims)
        self.assertTrue(result.rule_decisions)

    def test_url_without_text_is_unclear_fetch_gap(self) -> None:
        result = asyncio.run(analyze_tweet(TweetInput(tweet_url="https://x.com/example/status/123456")))

        self.assertEqual(result.verdict, Verdict.UNCLEAR)
        self.assertEqual(result.tweet_id, "123456")
        self.assertIn("Tweet URL was recorded", result.reasoning)


if __name__ == "__main__":
    unittest.main()
