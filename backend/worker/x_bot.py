from __future__ import annotations

import re
from dataclasses import dataclass

from backend.core.analysis_pipeline import analyze_tweet
from backend.core.schemas import TweetInput
from backend.db.repository import save_analysis
from backend.settings import Settings, get_settings


URL_RE = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/\S+/status/\d+", re.IGNORECASE)


@dataclass(slots=True)
class BotMention:
    mention_id: str
    author_id: str
    text: str
    target_tweet_text: str | None = None


class XBotWorker:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def handle_mention(self, mention: BotMention) -> str:
        target_url = self._extract_target_url(mention.text)
        result = await analyze_tweet(
            TweetInput(
                text=mention.target_tweet_text,
                tweet_url=target_url,
                source="x_bot",
                requester_id=mention.author_id,
            )
        )
        save_analysis(result, self.settings)
        return self.format_reply(result.analysis_id, result.verdict.value, result.confidence)

    def format_reply(self, analysis_id: str, verdict: str, confidence: float) -> str:
        verdict_label = verdict.replace("_", " ")
        detail_url = f"{self.settings.website_base_url.rstrip('/')}/history?analysis={analysis_id}"
        return f"Credibility signal: {verdict_label} ({confidence:.0%}). Full context: {detail_url}"

    def _extract_target_url(self, mention_text: str) -> str | None:
        match = URL_RE.search(mention_text)
        return match.group(0) if match else None

    async def poll_mentions(self) -> None:
        if not self.settings.x_api_bearer_token:
            raise RuntimeError("Set X_API_BEARER_TOKEN before enabling live mention polling.")
        raise NotImplementedError("Live X polling/webhook integration is intentionally deferred until API access is confirmed.")
