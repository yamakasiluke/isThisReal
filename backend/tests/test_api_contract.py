from __future__ import annotations

import importlib
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.settings import get_settings


class ApiContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.previous_database_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = f"sqlite:///{Path(cls.temp_dir.name) / 'api-test.db'}"
        get_settings.cache_clear()

        main_module = importlib.import_module("backend.api.main")
        cls.main_module = importlib.reload(main_module)
        cls.client = TestClient(cls.main_module.app)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.previous_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = cls.previous_database_url
        get_settings.cache_clear()
        cls.temp_dir.cleanup()

    def test_health_returns_ok(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_analyze_history_detail_and_review_contract(self) -> None:
        analysis_response = self.client.post(
            "/analyze",
            json={
                "text": "People are saying 82 percent disappeared, share before they delete this.",
                "source": "api-test",
            },
        )

        self.assertEqual(analysis_response.status_code, 200)
        analysis_payload = analysis_response.json()
        self.assertEqual(analysis_payload["verdict"], "suspicious")
        self.assertIn("analysis_id", analysis_payload)

        history_response = self.client.get("/analyses?limit=1")
        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(history_response.json()[0]["analysis_id"], analysis_payload["analysis_id"])

        detail_response = self.client.get(f"/analyses/{analysis_payload['analysis_id']}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["analysis_id"], analysis_payload["analysis_id"])

        review_response = self.client.post(
            "/reviews",
            json={
                "user_id": "reviewer-1",
                "analysis_id": analysis_payload["analysis_id"],
                "verdict": "suspicious",
                "confidence": 0.8,
                "comment": "Looks risky.",
            },
        )
        self.assertEqual(review_response.status_code, 200)
        self.assertEqual(review_response.json()["verdict"], "suspicious")

    def test_analyze_requires_text_or_url(self) -> None:
        response = self.client.post("/analyze", json={})

        self.assertEqual(response.status_code, 422)

    def test_missing_analysis_returns_404(self) -> None:
        response = self.client.get("/analyses/not-real")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
