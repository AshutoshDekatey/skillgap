from __future__ import annotations

from collections import defaultdict

from questions import QUESTIONS, SKILL_LABELS, TRACK_LABELS


def questions_for_track(track: str) -> list[dict]:
    return [question for question in QUESTIONS if question["track"] == track]


def get_question(question_id: int) -> dict:
    return next(question for question in QUESTIONS if question["id"] == question_id)


def diagnostic_question_ids(track: str) -> list[int]:
    return [q["id"] for q in questions_for_track(track) if q["diagnostic"]]


def question_statuses(attempts: list[dict]) -> dict[int, dict[str, int | bool]]:
    """Summarize whether each attempted question is resolved and how often it was missed."""
    statuses: defaultdict[int, dict[str, int | bool]] = defaultdict(
        lambda: {"attempts": 0, "wrong": 0, "correct": False}
    )
    for attempt in attempts:
        status = statuses[attempt["question_id"]]
        status["attempts"] = int(status["attempts"]) + 1
        if attempt["correct"]:
            status["correct"] = True
        else:
            status["wrong"] = int(status["wrong"]) + 1
    return dict(statuses)


def get_mastery(attempts: list[dict], track: str) -> dict[str, dict[str, float | int]]:
    """Estimate skill mastery from unique questions, so repeated misses do not distort the denominator."""
    statuses = question_statuses(attempts)
    mastery: dict[str, dict[str, float | int]] = {}
    for skill in SKILL_LABELS[track]:
        skill_questions = [q for q in questions_for_track(track) if q["skill"] == skill]
        attempted_ids = [q["id"] for q in skill_questions if q["id"] in statuses]
        correct_ids = [qid for qid in attempted_ids if bool(statuses[qid]["correct"])]
        unresolved = [qid for qid in attempted_ids if not bool(statuses[qid]["correct"])]
        if not attempted_ids:
            score = 0.0
        else:
            # Neutral prior prevents a single answer from displaying an extreme 0% or 100%.
            score = ((len(correct_ids) + 0.5) / (len(attempted_ids) + 1.0)) * 100
        mastery[skill] = {
            "score": round(score, 1),
            "attempted": len(attempted_ids),
            "correct": len(correct_ids),
            "unresolved": len(unresolved),
            "total": len(skill_questions),
        }
    return mastery


def build_practice_queue(
    track: str,
    attempts: list[dict],
    mastery: dict[str, dict[str, float | int]],
    count: int = 10,
) -> list[int]:
    """
    Select weak-skill questions, returning unresolved wrong answers but permanently
    excluding any question that has ever been answered correctly.
    """
    statuses = question_statuses(attempts)
    eligible = [
        q for q in questions_for_track(track)
        if not bool(statuses.get(q["id"], {}).get("correct", False))
    ]

    def priority(question: dict) -> tuple[float, int, int, int]:
        status = statuses.get(question["id"], {"attempts": 0, "wrong": 0})
        attempts_count = int(status["attempts"])
        wrong_count = int(status["wrong"])
        skill_score = float(mastery[question["skill"]]["score"])
        # Unresolved misses are deliberately brought back. Weak skills still
        # dominate the ordering, while repeated exposure prevents starvation.
        return (
            skill_score - min(wrong_count, 3) * 24 + attempts_count * 4,
            0 if wrong_count else 1,
            attempts_count,
            question["difficulty"],
        )

    return [q["id"] for q in sorted(eligible, key=priority)[:count]]


def readiness_summary(mastery: dict[str, dict[str, float | int]]) -> dict:
    measured = [value for value in mastery.values() if int(value["attempted"]) > 0]
    readiness = round(sum(float(v["score"]) for v in measured) / len(measured)) if measured else 0
    strongest = max(mastery, key=lambda skill: float(mastery[skill]["score"]))
    weakest = min(
        mastery,
        key=lambda skill: (float(mastery[skill]["score"]), -int(mastery[skill]["unresolved"])),
    )
    completed = sum(int(value["correct"]) for value in mastery.values())
    unresolved = sum(int(value["unresolved"]) for value in mastery.values())
    total = sum(int(value["total"]) for value in mastery.values())
    return {
        "readiness": readiness,
        "strongest": strongest,
        "weakest": weakest,
        "completed": completed,
        "unresolved": unresolved,
        "total": total,
    }


__all__ = [
    "SKILL_LABELS", "TRACK_LABELS", "build_practice_queue", "diagnostic_question_ids",
    "get_mastery", "get_question", "question_statuses", "questions_for_track",
    "readiness_summary",
]
