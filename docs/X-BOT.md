# X Bot

The current bot code is a thin adapter around the shared analysis backend. It is intentionally conservative so the website and backend can mature before public X/Twitter automation is enabled.

## Current Behavior

`backend/worker/x_bot.py` supports:

- parsing an X/Twitter status URL from a mention text
- passing tweet text or URL into the shared analysis core
- storing the analysis through the same repository path used by the website
- formatting a short reply with verdict, confidence, and a website link

Example reply:

```text
Credibility signal: suspicious (90%). Full context: http://localhost:3000/history?analysis=...
```

## Not Implemented Yet

- live mention polling
- webhook registration
- X API write/posting flow
- rate-limit backoff
- moderation review queue

Calling `poll_mentions()` without credentials raises a clear runtime error. Calling it with credentials currently raises `NotImplementedError` because live X integration is deliberately deferred.

## Launch Caution

Use mention-based or explicit opt-in behavior. Do not build unsolicited replies into the MVP. Public bot copy should say the bot provides a credibility signal, not a final fact-check.

## Future Checklist

- Confirm X API tier supports the read and write operations needed.
- Add a queue for mentions.
- Add retry and backoff handling.
- Add abuse limits and moderation logging.
- Keep website results as the full explanation surface; keep bot replies short.
