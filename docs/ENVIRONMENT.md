# Environment

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

## Backend Variables

| Variable | Default | Required | Notes |
| --- | --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./data/isthisreal.db` | yes | Only `sqlite:///` URLs are supported by the current MVP helper. |
| `LLM_PROVIDER` | `heuristic` | yes | Use `heuristic` locally. Use `openai` when an API key is configured. |
| `LLM_MODEL` | `gpt-4o-mini` | no | Used by the OpenAI path. |
| `LLM_TEMPERATURE` | `0.1` | no | Used by the OpenAI path. |
| `OPENAI_API_KEY` | empty | only for OpenAI | Leave empty for heuristic mode. |
| `WEBSITE_BASE_URL` | `http://localhost:3000` | yes | Used when the bot formats result links. |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000` | yes | Comma-separated browser origins allowed to call the backend. |
| `X_API_BEARER_TOKEN` | empty | future bot polling | Live mention polling is not implemented yet. |
| `X_API_KEY` | empty | future bot posting | Reserved for future X integration. |
| `X_API_SECRET` | empty | future bot posting | Reserved for future X integration. |
| `X_ACCESS_TOKEN` | empty | future bot posting | Reserved for future X integration. |
| `X_ACCESS_TOKEN_SECRET` | empty | future bot posting | Reserved for future X integration. |

## Local Defaults

For local work, keep:

```env
LLM_PROVIDER=heuristic
DATABASE_URL=sqlite:///./data/isthisreal.db
BACKEND_CORS_ORIGINS=http://localhost:3000
WEBSITE_BASE_URL=http://localhost:3000
```

## Deployment Notes

- Set `BACKEND_CORS_ORIGINS` to the deployed website origin.
- Set `WEBSITE_BASE_URL` to the deployed website URL so bot replies link to the right place.
- Use persistent storage for the SQLite database if staying on SQLite during early deployment.
- Move to PostgreSQL before relying on concurrent production traffic; the current helper is SQLite-only.
