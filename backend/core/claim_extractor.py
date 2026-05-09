from __future__ import annotations

import re

from backend.core.schemas import ClaimType, ExtractedClaim


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
NUMBER_RE = re.compile(r"\b\d+(?:[,.]\d+)*(?:%| percent| million| billion|k)?\b", re.IGNORECASE)
ATTRIBUTION_RE = re.compile(r"\b(said|says|according to|reported|claims?|announced)\b", re.IGNORECASE)
TEMPORAL_RE = re.compile(r"\b(today|tonight|tomorrow|yesterday|now|just|breaking|this week)\b", re.IGNORECASE)
OPINION_RE = re.compile(r"\b(i think|imo|opinion|feels like|seems like)\b", re.IGNORECASE)


def extract_claims(text: str) -> list[ExtractedClaim]:
    if not text.strip():
        return []

    chunks = [chunk.strip() for chunk in SENTENCE_SPLIT_RE.split(text.strip()) if chunk.strip()]
    claims: list[ExtractedClaim] = []
    for chunk in chunks[:6]:
        claim_type = ClaimType.FACTUAL
        confidence = 0.58
        if OPINION_RE.search(chunk):
            claim_type = ClaimType.OPINION
            confidence = 0.42
        elif NUMBER_RE.search(chunk):
            claim_type = ClaimType.STATISTICAL
            confidence = 0.68
        elif ATTRIBUTION_RE.search(chunk):
            claim_type = ClaimType.ATTRIBUTED
            confidence = 0.64
        elif TEMPORAL_RE.search(chunk):
            claim_type = ClaimType.TEMPORAL
            confidence = 0.6

        claims.append(ExtractedClaim(text=chunk, claim_type=claim_type, confidence=confidence))

    return claims
