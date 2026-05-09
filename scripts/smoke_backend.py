from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.api.main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/health")
    health.raise_for_status()

    analysis = client.post(
        "/analyze",
        json={
            "text": "BREAKING people are saying 75 percent vanished, share before they delete this.",
            "source": "smoke",
        },
    )
    analysis.raise_for_status()
    payload = analysis.json()

    history = client.get("/analyses?limit=1")
    history.raise_for_status()

    print("health:", health.json()["status"])
    print("analysis:", payload["verdict"], payload["confidence"])
    print("history_count:", len(history.json()))


if __name__ == "__main__":
    main()
