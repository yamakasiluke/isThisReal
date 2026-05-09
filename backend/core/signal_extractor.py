from __future__ import annotations

import re

from backend.core.schemas import Signal, TweetMetadata


URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
NUMBER_RE = re.compile(r"\b\d+(?:[,.]\d+)*(?:%| percent| million| billion|k)?\b", re.IGNORECASE)
BREAKING_RE = re.compile(r"\b(breaking|urgent|just in|developing)\b", re.IGNORECASE)
VAGUE_SOURCE_RE = re.compile(
    r"\b(they say|people are saying|sources say|heard that|rumou?r|unconfirmed|apparently)\b",
    re.IGNORECASE,
)
VIRAL_SHARE_RE = re.compile(
    r"\b(share before|they deleted|media won't show|wake up|do your own research|spread this)\b",
    re.IGNORECASE,
)
ATTRIBUTION_RE = re.compile(r"\b(according to|reported by|said|announced|published by)\b", re.IGNORECASE)
MEDIA_MARKER_RE = re.compile(r"\b(video|image|photo|screenshot|clip)\b", re.IGNORECASE)


def _bool_signal(name: str, value: bool, weight: float, description: str, priority: str = "medium") -> Signal:
    return Signal(name=name, value=value, weight=weight if value else 0.0, priority=priority, description=description)


def extract_signals(text: str, metadata: TweetMetadata | None = None) -> list[Signal]:
    metadata = metadata or TweetMetadata()
    has_link = bool(URL_RE.search(text))
    has_number = bool(NUMBER_RE.search(text))
    has_attribution = bool(ATTRIBUTION_RE.search(text))
    signals = [
        _bool_signal(
            "has_external_link",
            has_link,
            -0.08,
            "Tweet includes an external link that may provide evidence.",
            "low",
        ),
        _bool_signal(
            "breaking_language",
            bool(BREAKING_RE.search(text)),
            0.09,
            "Tweet uses urgent or breaking-news framing.",
        ),
        _bool_signal(
            "vague_source_language",
            bool(VAGUE_SOURCE_RE.search(text)),
            0.16,
            "Tweet relies on vague or unconfirmed sourcing language.",
            "high",
        ),
        _bool_signal(
            "viral_share_language",
            bool(VIRAL_SHARE_RE.search(text)),
            0.2,
            "Tweet encourages viral sharing or implies suppression without evidence.",
            "high",
        ),
        _bool_signal(
            "numeric_claim",
            has_number,
            0.04,
            "Tweet includes a numeric or statistical claim.",
        ),
        _bool_signal(
            "numeric_claim_without_source",
            has_number and not has_link and not has_attribution,
            0.18,
            "Tweet includes a numeric claim without an obvious source.",
            "high",
        ),
        _bool_signal(
            "quote_or_attribution_present",
            has_attribution,
            -0.04,
            "Tweet includes attribution language.",
            "low",
        ),
        _bool_signal(
            "all_caps_emphasis",
            _has_all_caps_phrase(text),
            0.08,
            "Tweet contains all-caps emphasis.",
        ),
        _bool_signal(
            "media_reference",
            bool(metadata.has_media) or bool(MEDIA_MARKER_RE.search(text)),
            0.02,
            "Tweet references or includes media that may need separate verification.",
        ),
        _bool_signal(
            "verified_author",
            bool(metadata.author_verified),
            -0.05,
            "Author metadata indicates a verified account.",
            "low",
        ),
    ]

    if metadata.author_account_age_days is not None:
        signals.append(
            Signal(
                name="new_author_account",
                value=metadata.author_account_age_days < 30,
                weight=0.12 if metadata.author_account_age_days < 30 else 0.0,
                priority="medium",
                description="Author account appears to be less than 30 days old.",
            )
        )

    if metadata.follower_count is not None and metadata.following_count is not None:
        ratio = metadata.follower_count / max(metadata.following_count, 1)
        signals.append(
            Signal(
                name="low_follower_ratio",
                value=round(ratio, 3),
                weight=0.08 if metadata.follower_count < 100 and ratio < 0.25 else 0.0,
                priority="low",
                description="Follower/following metadata suggests limited account credibility.",
            )
        )

    return signals


def _has_all_caps_phrase(text: str) -> bool:
    words = re.findall(r"\b[A-Z]{4,}\b", text)
    return len(words) >= 2
