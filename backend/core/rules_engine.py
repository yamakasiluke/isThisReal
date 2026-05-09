from __future__ import annotations

from dataclasses import dataclass

from backend.core.schemas import RuleDecision, Signal, Verdict, clamp


DEFAULT_RULESET_VERSION = "rules_v1"


@dataclass(frozen=True, slots=True)
class DeterministicRule:
    rule_id: str
    signal_name: str
    name: str
    description: str
    score_delta: float
    verdict_hint: Verdict
    confidence_boost: float = 0.0


DEFAULT_RULES: tuple[DeterministicRule, ...] = (
    DeterministicRule(
        rule_id="rule.has_source_link.v1",
        signal_name="has_external_link",
        name="Source link present",
        description="External links do not prove truth, but they make the claim easier to inspect.",
        score_delta=-0.08,
        verdict_hint=Verdict.LIKELY_TRUE,
        confidence_boost=0.02,
    ),
    DeterministicRule(
        rule_id="rule.vague_source.v1",
        signal_name="vague_source_language",
        name="Vague sourcing language",
        description="Vague sourcing is a common marker for unverifiable claims.",
        score_delta=0.16,
        verdict_hint=Verdict.SUSPICIOUS,
        confidence_boost=0.06,
    ),
    DeterministicRule(
        rule_id="rule.viral_share.v1",
        signal_name="viral_share_language",
        name="Viral sharing pressure",
        description="Pressure to share before evidence is checked raises credibility risk.",
        score_delta=0.2,
        verdict_hint=Verdict.SUSPICIOUS,
        confidence_boost=0.08,
    ),
    DeterministicRule(
        rule_id="rule.unsourced_number.v1",
        signal_name="numeric_claim_without_source",
        name="Unsourced numeric claim",
        description="Statistical claims need clear sourcing to be credible.",
        score_delta=0.18,
        verdict_hint=Verdict.SUSPICIOUS,
        confidence_boost=0.07,
    ),
    DeterministicRule(
        rule_id="rule.verified_author.v1",
        signal_name="verified_author",
        name="Verified author metadata",
        description="Verified author metadata slightly reduces risk but does not settle truth.",
        score_delta=-0.05,
        verdict_hint=Verdict.LIKELY_TRUE,
        confidence_boost=0.01,
    ),
    DeterministicRule(
        rule_id="rule.new_author.v1",
        signal_name="new_author_account",
        name="New author account",
        description="New accounts deserve extra caution for high-impact factual claims.",
        score_delta=0.12,
        verdict_hint=Verdict.SUSPICIOUS,
        confidence_boost=0.03,
    ),
)


def evaluate_rules(signals: list[Signal], rules: tuple[DeterministicRule, ...] = DEFAULT_RULES) -> list[RuleDecision]:
    signal_map = {signal.name: signal for signal in signals}
    decisions: list[RuleDecision] = []
    for rule in rules:
        signal = signal_map.get(rule.signal_name)
        triggered = bool(signal and signal.value and signal.weight != 0.0)
        if not triggered:
            continue
        decisions.append(
            RuleDecision(
                rule_id=rule.rule_id,
                name=rule.name,
                triggered=True,
                score_delta=rule.score_delta,
                verdict_hint=rule.verdict_hint,
                confidence_boost=rule.confidence_boost,
                reason=rule.description,
            )
        )
    return decisions


def compose_rule_score(decisions: list[RuleDecision]) -> float:
    return clamp(0.5 + sum(decision.score_delta for decision in decisions), 0.05, 0.95)


def strongest_rule_boost(decisions: list[RuleDecision]) -> float:
    if not decisions:
        return 0.0
    return max(decision.confidence_boost for decision in decisions)
