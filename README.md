# Is This Real

Credibility checker for tweets, with a shared backend that powers a website and an X/Twitter mention bot.

The MVP does not claim to be an authoritative fact-checker. It returns a defensible credibility assessment: `likely_true`, `suspicious`, or `unclear`, plus confidence, signals, extracted claims, and an audit trail.

## Documentation

- [Setup](docs/SETUP.md) - local prerequisites, backend and website startup, and common failures.
- [Testing](docs/TESTING.md) - unit, API, database, bot, smoke, and frontend verification plan.
- [Architecture](docs/ARCHITECTURE.md) - how website and bot requests flow through the shared analysis core.
- [API](docs/API.md) - endpoint reference and example requests.
- [Environment](docs/ENVIRONMENT.md) - supported environment variables and deployment notes.
- [X Bot](docs/X-BOT.md) - current mention-bot behavior, deferred live polling, and launch cautions.
- [Deployment](docs/DEPLOYMENT.md) - local-to-production checklist and smoke tests.
- [Launch Copy](docs/LAUNCH-COPY.md) - short X/Twitter post options.

## Project Layout

- `backend/` - FastAPI service, analysis core, SQLite persistence, and X bot adapter.
- `web/` - Next.js website for submitting tweets, reviewing results, and viewing history/admin surfaces.
- `docs/` - setup, testing, architecture, deployment, and launch copy.
- `plan/` - planning and requirement notes.

## Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
uvicorn backend.api.main:app --reload
```

Run the backend tests:

```bash
python -m unittest discover backend/tests
```

Run the backend smoke check:

```bash
python scripts/smoke_backend.py
```

The backend works without an LLM key by using a local heuristic judge. Set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` when you are ready to call the OpenAI API.

## Website

```bash
cd web
pnpm install
pnpm run dev
```

The website expects the backend at `http://localhost:8000` unless `NEXT_PUBLIC_API_BASE_URL` is set.

This repo is verified with Node.js and pnpm. npm may also work, but pnpm is the supported local path in this workspace. See [Setup](docs/SETUP.md).

## X/Twitter Bot

The first bot adapter is intentionally thin. It parses explicit mentions, calls the same analysis core used by the website, and formats a short reply that links to the website for the full result. Production polling/webhook code should be added only after X API credentials and rate limits are confirmed.
