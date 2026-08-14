from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: Path) -> None:
    with connect(db_path) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                goal TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                track TEXT NOT NULL,
                skill TEXT NOT NULL,
                correct INTEGER NOT NULL,
                confidence TEXT NOT NULL,
                mode TEXT NOT NULL,
                attempted_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(attempts)")}
        if "track" not in columns:
            # Keep V1 attempts out of V2 scoring because its skill taxonomy changed.
            connection.execute("ALTER TABLE attempts ADD COLUMN track TEXT NOT NULL DEFAULT 'legacy_v1'")


def create_or_get_user(db_path: Path, name: str, track: str) -> int:
    with connect(db_path) as connection:
        existing = connection.execute("SELECT id FROM users WHERE name = ?", (name,)).fetchone()
        if existing:
            connection.execute("UPDATE users SET goal = ? WHERE id = ?", (track, existing["id"]))
            return int(existing["id"])
        cursor = connection.execute(
            "INSERT INTO users(name, goal, created_at) VALUES (?, ?, ?)",
            (name, track, datetime.now(timezone.utc).isoformat()),
        )
        return int(cursor.lastrowid)


def record_attempt(
    db_path: Path,
    user_id: int,
    question_id: int,
    track: str,
    skill: str,
    correct: bool,
    confidence: str,
    mode: str,
) -> None:
    with connect(db_path) as connection:
        connection.execute(
            """INSERT INTO attempts
               (user_id, question_id, track, skill, correct, confidence, mode, attempted_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, question_id, track, skill, int(correct), confidence, mode,
             datetime.now(timezone.utc).isoformat()),
        )


def get_attempts(db_path: Path, user_id: int, track: str) -> list[dict]:
    with connect(db_path) as connection:
        rows = connection.execute(
            """SELECT question_id, track, skill, correct, confidence, mode, attempted_at
               FROM attempts WHERE user_id = ? AND track = ? ORDER BY attempted_at""",
            (user_id, track),
        ).fetchall()
    return [dict(row) for row in rows]


def get_attempted_question_ids(db_path: Path, user_id: int, track: str, mode: str) -> set[int]:
    with connect(db_path) as connection:
        rows = connection.execute(
            """SELECT DISTINCT question_id FROM attempts
               WHERE user_id = ? AND track = ? AND mode = ?""",
            (user_id, track, mode),
        ).fetchall()
    return {int(row["question_id"]) for row in rows}
