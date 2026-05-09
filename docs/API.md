# API

Base URL for local development: `http://localhost:8000`.

## Health

```http
GET /health
```

Response:

```json
{"status":"ok"}
```

## Analyze A Tweet

```http
POST /analyze
Content-Type: application/json
```

Request:

```json
{
  "text": "BREAKING people are saying 80 percent disappeared, share before they delete this.",
  "tweet_url": "https://x.com/example/status/123456",
  "source": "website",
  "requester_id": "optional-user-id"
}
```

At least one of `text` or `tweet_url` is required.

Response fields include:

- `analysis_id`
- `tweet_id`
- `verdict`
- `confidence`
- `reasoning`
- `claims`
- `signals`
- `rule_decisions`
- `suspicion_score`
- `prompt_version`
- `ruleset_version`
- `model_name`
- `disclaimer`

## List Recent Analyses

```http
GET /analyses?limit=25
```

Returns recent stored analysis summaries. `limit` is clamped between `1` and `100`.

## Get Analysis Detail

```http
GET /analyses/{analysis_id}
```

Returns the full stored analysis payload or `404` if it is not found.

## Add A Review

```http
POST /reviews
Content-Type: application/json
```

Request:

```json
{
  "user_id": "reviewer-1",
  "analysis_id": "existing-analysis-id",
  "verdict": "suspicious",
  "confidence": 0.8,
  "comment": "Reviewer note"
}
```

This records a human review and an audit event. Review validation and credit recalculation are planned follow-up work.
