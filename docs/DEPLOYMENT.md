# Deployment

This checklist separates local runnability from public deployment readiness.

## Backend Checklist

- Install Python 3.11+.
- Install dependencies with `pip install -e .`.
- Set production environment variables.
- Ensure `DATABASE_URL` points to persistent storage.
- Set `BACKEND_CORS_ORIGINS` to the deployed website origin.
- Run `python -m unittest discover backend/tests`.
- Run a deployed `GET /health` check.
- Run one deployed `POST /analyze` smoke request.

## Website Checklist

- Install Node.js 20+ and pnpm.
- Set `NEXT_PUBLIC_API_BASE_URL` to the deployed backend URL.
- Run `pnpm install`.
- Run `pnpm run build`.
- Confirm the home page loads.
- Submit one tweet text through the website and confirm the backend stores history.

## Bot Checklist

- Set `WEBSITE_BASE_URL` to the deployed website URL.
- Confirm the bot reply link points to the deployed website.
- Do not enable public polling until X API credentials, rate limits, and posting behavior are implemented and tested.

## Production Gaps To Close

- Move persistence beyond raw local SQLite for real traffic.
- Add structured application logging.
- Add rate limiting for `/analyze`.
- Add LLM timeout and malformed-response fallback tests.
- Add X API queue, retry, and moderation workflows.
