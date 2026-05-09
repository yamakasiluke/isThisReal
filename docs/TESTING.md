# Testing

The test plan keeps the project honest at three levels: core logic, service behavior, and run-readiness.

## Current Supported Command

From the repo root:

```bash
python -m unittest discover backend/tests
```

This runs tests for:

- Analysis pipeline verdict behavior.
- Deterministic rule scoring.
- User credit calculation and bounded confidence adjustment.
- FastAPI endpoint contracts.
- SQLite repository round trips.
- X bot mention handling and reply formatting.

## Backend Smoke Check

```bash
python scripts/smoke_backend.py
```

The smoke script verifies that the backend app can respond to `/health`, accept an `/analyze` request, and return history data.

## Test Layers

### Tier 1: Core Unit Tests

Files:

- `backend/tests/test_analysis_pipeline.py`
- `backend/tests/test_rules_engine.py`
- `backend/tests/test_user_credit.py`

These tests should stay fast and should not require network access or API keys.

### Tier 2: API Contract Tests

File:

- `backend/tests/test_api_contract.py`

Coverage targets:

- `GET /health`
- `POST /analyze`
- `GET /analyses`
- `GET /analyses/{analysis_id}`
- `POST /reviews`
- validation failure for empty analyze requests

### Tier 3: Persistence Tests

File:

- `backend/tests/test_repository.py`

Coverage targets:

- analysis save and lookup
- recent history listing
- review insertion
- audit row creation

### Tier 4: Bot Tests

File:

- `backend/tests/test_x_bot.py`

Coverage targets:

- X/Twitter URL extraction
- formatted reply links
- mention handling through the shared analysis core
- explicit failure when live polling is enabled without credentials

### Tier 5: Frontend Verification

Requires Node.js and pnpm:

```bash
cd web
pnpm install
pnpm run build
```

The frontend production build has been verified with pnpm. npm stalled during dependency metadata resolution in this workspace, so pnpm is the recommended path.

## Future Tests

- Malformed OpenAI response fallback.
- Rate-limit behavior for website and bot inputs.
- Concurrent analyze requests against the database.
- Labeled tweet evaluation set for false-positive and false-negative tracking.
