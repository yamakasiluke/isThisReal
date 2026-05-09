from __future__ import annotations

import re
from dataclasses import dataclass

from backend.core.schemas import TweetInput, TweetMetadata


TWEET_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:x|twitter)\.com/(?P<handle>[A-Za-z0-9_]+)/status/(?P<id>\d+)",
    re.IGNORECASE,
)


@dataclass(slots=True)
class NormalizedTweet:
    text: str
    tweet_id: str | None
    tweet_url: str | None
    metadata: TweetMetadata
    has_fetch_gap: bool


def extract_tweet_id(tweet_url: str | None) -> str | None:
    if not tweet_url:
        return None
    match = TWEET_URL_RE.search(tweet_url.strip())
    if not match:
        return None
    return match.group("id")


def normalize_tweet_input(tweet_input: TweetInput) -> NormalizedTweet:
    text = (tweet_input.text or "").strip()
    tweet_url = tweet_input.tweet_url.strip() if tweet_input.tweet_url else None
    metadata = tweet_input.metadata or TweetMetadata()
    tweet_id = metadata.tweet_id or extract_tweet_id(tweet_url)

    if not text and tweet_url:
        text = ""

    if not text and not tweet_url:
        raise ValueError("Provide tweet text, a tweet URL, or both.")

    metadata.tweet_id = tweet_id
    return NormalizedTweet(
        text=text,
        tweet_id=tweet_id,
        tweet_url=tweet_url,
        metadata=metadata,
        has_fetch_gap=bool(tweet_url and not text),
    )
