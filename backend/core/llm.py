from __future__ import annotations

import json
from typing import Protocol

from backend.core.schemas import ExtractedClaim, LLMJudgment, Signal, Verdict, clamp
from backend.settings import Settings, get_settings


class LLMJudge(Protocol):
    async def judge(
        self,
        tweet_text: str,
        claims: list[ExtractedClaim],
        signals: list[Signal],
    ) -> LLMJudgment:
        ...


class HeuristicLLMClient:
    model_name = "heuristic-offline"

    async def judge(
        self,
        tweet_text: str,
        claims: list[ExtractedClaim],
        signals: list[Signal],
    ) -> LLMJudgment:
        if not tweet_text.strip():
            return LLMJudgment(
                verdict=Verdict.UNCLEAR,
                confidence=0.55,
                reasoning="Tweet text is not available yet, so the system can only record the URL and wait for fetched content.",
                caveats=["Configure X API lookup or paste tweet text for a fuller assessment."],
                model_name=self.model_name,
            )

        signal_score = clamp(0.5 + sum(signal.weight for signal in signals), 0.05, 0.95)
        if signal_score >= 0.68:
            verdict = Verdict.SUSPICIOUS
            confidence = min(0.82, signal_score)
            reasoning = "The tweet contains multiple credibility-risk signals such as vague sourcing, viral pressure, or unsourced numeric claims."
        elif signal_score <= 0.36:
            verdict = Verdict.LIKELY_TRUE
            confidence = min(0.74, 1 - signal_score)
            reasoning = "The tweet includes fewer credibility-risk signals and has some inspectable context such as attribution or links."
        else:
            verdict = Verdict.UNCLEAR
            confidence = 0.56
            reasoning = "The available signals are mixed or weak, so the claim needs more evidence before a stronger call."

        caveats = []
        if any(signal.name == "media_reference" and signal.value for signal in signals):
            caveats.append("Media authenticity is not verified by this MVP pipeline.")
        if not claims:
            caveats.append("No concrete factual claim was extracted from the text.")

        return LLMJudgment(
            verdict=verdict,
            confidence=round(confidence, 3),
            reasoning=reasoning,
            caveats=caveats,
            model_name=self.model_name,
        )


class OpenAIChatClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.model_name = self.settings.llm_model

    async def judge(
        self,
        tweet_text: str,
        claims: list[ExtractedClaim],
        signals: list[Signal],
    ) -> LLMJudgment:
        if not self.settings.openai_api_key:
            return await HeuristicLLMClient().judge(tweet_text, claims, signals)

        import httpx

        system_prompt = (
            "You judge whether a tweet is likely true, suspicious, or unclear. "
            "Return compact JSON with verdict, confidence, reasoning, and caveats. "
            "Do not claim certainty without evidence."
        )
        payload = {
            "model": self.settings.llm_model,
            "temperature": self.settings.llm_temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "tweet_text": tweet_text,
                            "claims": [claim.text for claim in claims],
                            "signals": [
                                {"name": signal.name, "value": signal.value, "weight": signal.weight}
                                for signal in signals
                            ],
                            "allowed_verdicts": [verdict.value for verdict in Verdict],
                        }
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return LLMJudgment(
            verdict=Verdict(parsed.get("verdict", Verdict.UNCLEAR.value)),
            confidence=clamp(float(parsed.get("confidence", 0.5))),
            reasoning=str(parsed.get("reasoning", "The model returned no reasoning."))[:900],
            caveats=[str(item)[:240] for item in parsed.get("caveats", [])[:5]],
            model_name=self.model_name,
        )


def create_llm_client(settings: Settings | None = None) -> LLMJudge:
    settings = settings or get_settings()
    if settings.llm_provider == "openai":
        return OpenAIChatClient(settings)
    return HeuristicLLMClient()
