from __future__ import annotations

from uuid import uuid4

from backend.core.claim_extractor import extract_claims
from backend.core.llm import LLMJudge, create_llm_client
from backend.core.normalizer import normalize_tweet_input
from backend.core.rules_engine import DEFAULT_RULESET_VERSION, compose_rule_score, evaluate_rules, strongest_rule_boost
from backend.core.schemas import AnalysisResult, LLMJudgment, TweetInput, UserCreditSnapshot, UserReview, Verdict, clamp
from backend.core.signal_extractor import extract_signals
from backend.core.user_credit import apply_credit_to_confidence
from backend.settings import Settings, get_settings


PROMPT_VERSION = "tweet_judge_v1"


class AnalysisPipeline:
    def __init__(self, settings: Settings | None = None, llm_client: LLMJudge | None = None) -> None:
        self.settings = settings or get_settings()
        self.llm_client = llm_client or create_llm_client(self.settings)

    async def analyze(
        self,
        tweet_input: TweetInput,
        user_reviews: list[UserReview] | None = None,
        credit_snapshots: dict[str, UserCreditSnapshot] | None = None,
    ) -> AnalysisResult:
        normalized = normalize_tweet_input(tweet_input)
        claims = extract_claims(normalized.text)
        signals = extract_signals(normalized.text, normalized.metadata)
        decisions = evaluate_rules(signals)
        rule_score = compose_rule_score(decisions)
        llm_judgment = await self.llm_client.judge(normalized.text, claims, signals)
        suspicion_score = _merge_scores(rule_score, llm_judgment)
        verdict = _score_to_verdict(suspicion_score, normalized.has_fetch_gap)
        confidence = _score_to_confidence(suspicion_score, verdict, llm_judgment, strongest_rule_boost(decisions))

        if user_reviews and credit_snapshots:
            confidence = apply_credit_to_confidence(confidence, verdict, user_reviews, credit_snapshots)

        reasoning = _compose_reasoning(normalized.has_fetch_gap, verdict, llm_judgment, decisions)
        return AnalysisResult(
            analysis_id=str(uuid4()),
            input=tweet_input,
            tweet_id=normalized.tweet_id,
            verdict=verdict,
            confidence=round(confidence, 3),
            reasoning=reasoning,
            claims=claims,
            signals=signals,
            rule_decisions=decisions,
            llm_judgment=llm_judgment,
            suspicion_score=round(suspicion_score, 3),
            prompt_version=PROMPT_VERSION,
            ruleset_version=DEFAULT_RULESET_VERSION,
            model_name=llm_judgment.model_name,
        )


async def analyze_tweet(
    tweet_input: TweetInput,
    settings: Settings | None = None,
    llm_client: LLMJudge | None = None,
) -> AnalysisResult:
    return await AnalysisPipeline(settings=settings, llm_client=llm_client).analyze(tweet_input)


def _merge_scores(rule_score: float, llm_judgment: LLMJudgment) -> float:
    llm_score_by_verdict = {
        Verdict.SUSPICIOUS: 0.76,
        Verdict.UNCLEAR: 0.5,
        Verdict.LIKELY_TRUE: 0.28,
    }
    llm_score = llm_score_by_verdict[llm_judgment.verdict]
    confidence_weight = clamp(llm_judgment.confidence, 0.35, 0.85)
    rule_weight = 1 - (confidence_weight * 0.62)
    combined = (llm_score * confidence_weight * 0.62) + (rule_score * rule_weight)
    return clamp(combined, 0.05, 0.95)


def _score_to_verdict(score: float, has_fetch_gap: bool) -> Verdict:
    if has_fetch_gap:
        return Verdict.UNCLEAR
    if score >= 0.64:
        return Verdict.SUSPICIOUS
    if score <= 0.36:
        return Verdict.LIKELY_TRUE
    return Verdict.UNCLEAR


def _score_to_confidence(score: float, verdict: Verdict, llm_judgment: LLMJudgment, rule_boost: float) -> float:
    if verdict == Verdict.UNCLEAR:
        return clamp(0.48 + abs(score - 0.5) * 0.45 + rule_boost, 0.35, 0.68)
    distance = abs(score - 0.5)
    return clamp(0.5 + distance * 0.9 + (llm_judgment.confidence * 0.18) + rule_boost, 0.52, 0.9)


def _compose_reasoning(
    has_fetch_gap: bool,
    verdict: Verdict,
    llm_judgment: LLMJudgment,
    decisions: list,
) -> str:
    if has_fetch_gap:
        return "Tweet URL was recorded, but tweet text was not available to inspect. Configure X API lookup or paste the tweet text for a stronger result."
    top_rules = ", ".join(decision.name for decision in decisions[:3])
    rule_phrase = f" Top triggered rules: {top_rules}." if top_rules else " No high-weight deterministic rules fired."
    verdict_phrase = verdict.value.replace("_", " ")
    return f"Verdict is {verdict_phrase}. {llm_judgment.reasoning}{rule_phrase}"
