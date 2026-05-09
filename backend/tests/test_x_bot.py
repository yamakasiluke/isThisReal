from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from backend.db.repository import list_recent_analyses
from backend.settings import Settings
from backend.worker.x_bot import BotMention, XBotWorker


class XBotWorkerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.settings = Settings(
            database_url=f"sqlite:///{Path(self.temp_dir.name) / 'bot-test.db'}",
            website_base_url="https://example.test",
        )
        self.worker = XBotWorker(settings=self.settings)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_extracts_target_url_from_mention(self) -> None:
        target = self.worker._extract_target_url("@bot check https://x.com/user/status/123456 please")

        self.assertEqual(target, "https://x.com/user/status/123456")

    def test_format_reply_uses_website_base_url(self) -> None:
        reply = self.worker.format_reply("analysis-1", "likely_true", 0.72)

        self.assertIn("Credibility signal: likely true (72%).", reply)
        self.assertIn("https://example.test/history?analysis=analysis-1", reply)

    def test_handle_mention_saves_analysis_and_returns_reply(self) -> None:
        reply = asyncio.run(
            self.worker.handle_mention(
                BotMention(
                    mention_id="m1",
                    author_id="user-1",
                    text="@bot check https://x.com/example/status/123456",
                    target_tweet_text="BREAKING people are saying 93 percent disappeared, share before they delete this.",
                )
            )
        )

        recent = list_recent_analyses(limit=1, settings=self.settings)
        self.assertIn("Credibility signal: suspicious", reply)
        self.assertEqual(recent[0]["source"], "x_bot")

    def test_poll_mentions_requires_credentials(self) -> None:
        with self.assertRaises(RuntimeError):
            asyncio.run(self.worker.poll_mentions())


if __name__ == "__main__":
    unittest.main()
