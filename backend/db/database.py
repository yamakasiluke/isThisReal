from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.settings import Settings, get_settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS tweets (
  tweet_key TEXT PRIMARY KEY,
  tweet_id TEXT,
  tweet_url TEXT,
  text TEXT,
  author_handle TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tweet_analyses (
  analysis_id TEXT PRIMARY KEY,
  tweet_key TEXT NOT NULL,
  source TEXT NOT NULL,
  verdict TEXT NOT NULL,
  confidence REAL NOT NULL,
  suspicion_score REAL NOT NULL,
  reasoning TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  ruleset_version TEXT NOT NULL,
  model_name TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(tweet_key) REFERENCES tweets(tweet_key)
);

CREATE TABLE IF NOT EXISTS extracted_claims (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id TEXT NOT NULL,
  claim_text TEXT NOT NULL,
  claim_type TEXT NOT NULL,
  confidence REAL NOT NULL,
  FOREIGN KEY(analysis_id) REFERENCES tweet_analyses(analysis_id)
);

CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id TEXT NOT NULL,
  name TEXT NOT NULL,
  value_json TEXT NOT NULL,
  weight REAL NOT NULL,
  priority TEXT NOT NULL,
  description TEXT NOT NULL,
  FOREIGN KEY(analysis_id) REFERENCES tweet_analyses(analysis_id)
);

CREATE TABLE IF NOT EXISTS rulesets (
  version TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  description TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rules (
  rule_id TEXT PRIMARY KEY,
  ruleset_version TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  score_delta REAL NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(ruleset_version) REFERENCES rulesets(version)
);

CREATE TABLE IF NOT EXISTS user_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  analysis_id TEXT NOT NULL,
  verdict TEXT NOT NULL,
  confidence REAL NOT NULL,
  comment TEXT,
  validation_status TEXT NOT NULL DEFAULT 'pending',
  validated_accuracy INTEGER,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(analysis_id) REFERENCES tweet_analyses(analysis_id)
);

CREATE TABLE IF NOT EXISTS user_credit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  delta REAL NOT NULL,
  new_score REAL NOT NULL,
  reason TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_credit_snapshots (
  user_id TEXT PRIMARY KEY,
  credibility_score REAL NOT NULL,
  reviews_count INTEGER NOT NULL,
  correct_count INTEGER NOT NULL,
  reason TEXT NOT NULL,
  last_updated TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  actor_id TEXT,
  analysis_id TEXT,
  old_value TEXT,
  new_value TEXT,
  reason TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def database_path(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    url = settings.database_url
    if not url.startswith("sqlite:///"):
        raise ValueError("This MVP database helper currently supports sqlite:/// URLs only.")
    path = Path(url.removeprefix("sqlite:///"))
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def connect(settings: Settings | None = None) -> sqlite3.Connection:
    path = database_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(settings: Settings | None = None) -> None:
    with connect(settings) as connection:
        connection.executescript(SCHEMA)
        connection.execute(
            "INSERT OR IGNORE INTO rulesets(version, status, description) VALUES (?, ?, ?)",
            ("rules_v1", "active", "Initial deterministic credibility rules."),
        )
