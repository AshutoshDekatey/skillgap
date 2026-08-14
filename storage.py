from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Path) -> None:
    with connect(db_path) as connection:
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
                skill TEXT NOT NULL,
                correct INTEGER NOT NULL,
                confidence TEXT NOT NULL,
                mode TEXT NOT NULL,
                attempted_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )


def create_or_get_user(db_path: Path, name: str, goal: str) -> int:
    with connect(db_path) as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE name = ?", (name,)
        ).fetchone()
        if existing:
            connection.execute("UPDATE users SET goal = ? WHERE id = ?", (goal, existing["id"]))
            return int(existing["id"])
        cursor = connection.execute(
            "INSERT INTO users(name, goal, created_at) VALUES (?, ?, ?)",
            (name, goal, datetime.now(timezone.utc).isoformat()),
        )
        return int(cursor.lastrowid)


def record_attempt(
    db_path: Path,
    user_id: int,
    question_id: int,
    skill: str,
    correct: bool,
    confidence: str,
    mode: str,
) -> None:
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO attempts(user_id, question_id, skill, correct, confidence, mode, attempted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                question_id,
                skill,
                int(correct),
                confidence,
                mode,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def get_attempts(db_path: Path, user_id: int) -> list[dict]:
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT question_id, skill, correct, confidence, mode, attempted_at
            FROM attempts WHERE user_id = ? ORDER BY attempted_at
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_attempted_question_ids(db_path: Path, user_id: int, mode: str) -> set[int]:
    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT DISTINCT question_id FROM attempts WHERE user_id = ? AND mode = ?",
            (user_id, mode),
        ).fetchall()
    return {int(row["question_id"]) for row in rows}
