from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any

from backend.core.schemas import AnalysisResult, Verdict, dataclass_to_dict
from backend.db.database import connect, initialize_database
from backend.settings import Settings


def save_analysis(result: AnalysisResult, settings: Settings | None = None) -> None:
    initialize_database(settings)
    payload = dataclass_to_dict(result)
    tweet_key = _tweet_key(result)
    with connect(settings) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO tweets(tweet_key, tweet_id, tweet_url, text, author_handle)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                tweet_key,
                result.tweet_id,
                result.input.tweet_url,
                result.input.text,
                result.input.metadata.author_handle if result.input.metadata else None,
            ),
        )
        connection.execute(
            """
            INSERT INTO tweet_analyses(
              analysis_id, tweet_key, source, verdict, confidence, suspicion_score, reasoning,
              prompt_version, ruleset_version, model_name, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.analysis_id,
                tweet_key,
                result.input.source,
                result.verdict.value,
                result.confidence,
                result.suspicion_score,
                result.reasoning,
                result.prompt_version,
                result.ruleset_version,
                result.model_name,
                json.dumps(payload),
                result.created_at,
            ),
        )
        for claim in result.claims:
            connection.execute(
                """
                INSERT INTO extracted_claims(analysis_id, claim_text, claim_type, confidence)
                VALUES (?, ?, ?, ?)
                """,
                (result.analysis_id, claim.text, claim.claim_type.value, claim.confidence),
            )
        for signal in result.signals:
            connection.execute(
                """
                INSERT INTO signals(analysis_id, name, value_json, weight, priority, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result.analysis_id,
                    signal.name,
                    json.dumps(signal.value),
                    signal.weight,
                    signal.priority,
                    signal.description,
                ),
            )
        connection.execute(
            """
            INSERT INTO audit_events(event_type, analysis_id, new_value, reason)
            VALUES (?, ?, ?, ?)
            """,
            ("analysis_created", result.analysis_id, result.verdict.value, "automated_analysis"),
        )


def list_recent_analyses(limit: int = 25, settings: Settings | None = None) -> list[dict[str, Any]]:
    initialize_database(settings)
    with connect(settings) as connection:
        rows = connection.execute(
            """
            SELECT analysis_id, tweet_key, source, verdict, confidence, suspicion_score, reasoning,
                   prompt_version, ruleset_version, model_name, created_at
            FROM tweet_analyses
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_analysis_payload(analysis_id: str, settings: Settings | None = None) -> dict[str, Any] | None:
    initialize_database(settings)
    with connect(settings) as connection:
        row = connection.execute(
            "SELECT payload_json FROM tweet_analyses WHERE analysis_id = ?",
            (analysis_id,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["payload_json"])


def add_review(
    user_id: str,
    analysis_id: str,
    verdict: Verdict,
    confidence: float,
    comment: str | None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    initialize_database(settings)
    with connect(settings) as connection:
        cursor = connection.execute(
            """
            INSERT INTO user_reviews(user_id, analysis_id, verdict, confidence, comment)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, analysis_id, verdict.value, confidence, comment),
        )
        review_id = cursor.lastrowid
        connection.execute(
            """
            INSERT INTO audit_events(event_type, actor_id, analysis_id, new_value, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("review_added", user_id, analysis_id, verdict.value, "user_review"),
        )
    return {"id": review_id, "user_id": user_id, "analysis_id": analysis_id, "verdict": verdict.value}


def _tweet_key(result: AnalysisResult) -> str:
    if result.tweet_id:
        return f"x:{result.tweet_id}"
    seed = result.input.text or result.input.tweet_url or result.analysis_id
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"manual:{digest}"


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}
