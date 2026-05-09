# Architecture

Is This Real uses one shared analysis backend for two user surfaces: the website and the X/Twitter bot adapter.

## Request Flow

```text
Website or X bot
  -> FastAPI route or bot worker
  -> TweetInput schema
  -> normalizer
  -> claim extractor
  -> signal extractor
  -> deterministic rules engine
  -> LLM or heuristic judge
  -> verdict composition
  -> SQLite persistence and audit event
  -> API response or bot reply
```

## Core Modules

- `backend/core/normalizer.py` extracts tweet IDs from X/Twitter URLs and validates input.
- `backend/core/claim_extractor.py` finds lightweight factual, temporal, statistical, attributed, and opinion claims.
- `backend/core/signal_extractor.py` extracts credibility signals such as vague sourcing, viral pressure, unsourced numbers, links, and account metadata.
- `backend/core/rules_engine.py` applies deterministic rule weights and rule explanations.
- `backend/core/llm.py` provides the LLM interface. The default is `HeuristicLLMClient`, which works offline.
- `backend/core/analysis_pipeline.py` composes the final verdict and confidence score.
- `backend/db/repository.py` stores analyses, claims, signals, reviews, and audit events.

## Verdict Model

The system returns one of three verdicts:

- `likely_true`
- `suspicious`
- `unclear`

This is intentionally not a binary real/fake model. The project returns a credibility signal with reasoning, not an authoritative fact-check.

## User Credit

Reviewer credit starts neutral and is bounded. Credit can adjust confidence in uncertain cases, but it should not flip a strong automated decision by itself.

## Current Limitations

- Live X/Twitter polling is not implemented yet.
- SQLite is the local persistence layer; production should use a managed persistent database.
- The default judge is heuristic so local development does not require an LLM key.
- Media authenticity and external evidence retrieval are outside the current MVP.
