import unittest

from backend.core.rules_engine import compose_rule_score, evaluate_rules
from backend.core.signal_extractor import extract_signals


class RulesEngineTest(unittest.TestCase):
    def test_vague_viral_unsourced_claim_increases_suspicion(self) -> None:
        text = "BREAKING people are saying 80 percent of ballots disappeared, share before they delete this"

        decisions = evaluate_rules(extract_signals(text))
        score = compose_rule_score(decisions)

        self.assertGreaterEqual(score, 0.8)
        self.assertIn("Vague sourcing language", {decision.name for decision in decisions})
        self.assertIn("Viral sharing pressure", {decision.name for decision in decisions})

    def test_source_link_reduces_suspicion(self) -> None:
        text = "The agency published the report today according to https://example.com/report"

        score = compose_rule_score(evaluate_rules(extract_signals(text)))

        self.assertLess(score, 0.5)


if __name__ == "__main__":
    unittest.main()
