# Setup

This project has two local runtimes: a Python backend and a Next.js website. The backend can run without external API keys by using the built-in heuristic judge.

## Prerequisites

- macOS, Linux, or another Unix-like shell.
- Python 3.11 or newer.
- Node.js 20 or newer and pnpm for the website.
- Optional: an OpenAI API key if `LLM_PROVIDER=openai` is enabled.
- Optional: X/Twitter API credentials for future live bot polling.

Check local tooling:

```bash
python3 --version
node --version
pnpm --version
```

If `node` or `pnpm` is missing, the backend can still run and test, but the website cannot be installed, started, or built yet.

## Backend

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
uvicorn backend.api.main:app --reload
```

The API starts on `http://localhost:8000` by default. Confirm it is alive:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Website

In a second terminal:

```bash
cd web
pnpm install
pnpm run dev
```

The website starts on `http://localhost:3000` and calls the backend at `http://localhost:8000` unless `NEXT_PUBLIC_API_BASE_URL` is set.

## Local Smoke Check

Run backend tests and the backend smoke script:

```bash
python -m unittest discover backend/tests
python scripts/smoke_backend.py
```

When Node/pnpm are available, run the website verification:

```bash
cd web
pnpm install
pnpm run build
```

## Common Failures

- `zsh: command not found: pnpm`: install pnpm before verifying the website. On macOS with Homebrew, run `brew install pnpm`.
- `Address already in use`: another process is using port `8000` or `3000`; stop it or choose another port.
- `CORS` errors in the browser: make sure `BACKEND_CORS_ORIGINS` includes the website origin.
- `OpenAI` errors: use `LLM_PROVIDER=heuristic` for local testing, or set `OPENAI_API_KEY` before using `LLM_PROVIDER=openai`.
