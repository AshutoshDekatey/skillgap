from __future__ import annotations

from collections import defaultdict

from questions import QUESTIONS, SKILL_LABELS, TRACK_LABELS


def questions_for_track(track: str) -> list[dict]:
    return [question for question in QUESTIONS if question["track"] == track]


def get_question(question_id: int) -> dict:
    return next(question for question in QUESTIONS if question["id"] == question_id)


def diagnostic_question_ids(track: str) -> list[int]:
    """Select the first two questions for every skill in a learner's track."""
    selected: list[int] = []
    counts: defaultdict[str, int] = defaultdict(int)
    for question in questions_for_track(track):
        skill = question["skill"]
        if counts[skill] < 2:
            selected.append(question["id"])
            counts[skill] += 1
    return selected


def get_mastery(attempts: list[dict], track: str) -> dict[str, dict[str, float | int]]:
    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for attempt in attempts:
        grouped[attempt["skill"]].append(attempt)

    confidence_weight = {"Guessing": 0.85, "Unsure": 0.95, "Fairly sure": 1.0, "Certain": 1.08}
    mastery: dict[str, dict[str, float | int]] = {}
    for skill in SKILL_LABELS[track]:
        skill_attempts = grouped[skill]
        if not skill_attempts:
            mastery[skill] = {"score": 0.0, "attempts": 0}
            continue

        earned = 0.0
        possible = 0.0
        for attempt in skill_attempts:
            weight = confidence_weight.get(attempt["confidence"], 1.0)
            possible += weight
            if attempt["correct"]:
                earned += weight
            elif attempt["confidence"] == "Guessing":
                earned += 0.08

        score = ((earned + 0.5) / (possible + 1.0)) * 100
        mastery[skill] = {"score": round(score, 1), "attempts": len(skill_attempts)}
    return mastery


def build_practice_queue(
    track: str,
    attempts: list[dict],
    mastery: dict[str, dict[str, float | int]],
    count: int = 5,
) -> list[int]:
    attempt_count: defaultdict[int, int] = defaultdict(int)
    for attempt in attempts:
        attempt_count[attempt["question_id"]] += 1

    def priority(question: dict) -> tuple[float, int, int]:
        score = float(mastery[question["skill"]]["score"])
        seen = attempt_count[question["id"]]
        diagnostic_penalty = 8 if question.get("diagnostic") else 0
        return (score + seen * 18 + diagnostic_penalty, seen, question["difficulty"])

    return [q["id"] for q in sorted(questions_for_track(track), key=priority)[:count]]


def readiness_summary(mastery: dict[str, dict[str, float | int]]) -> dict:
    measured = [values for values in mastery.values() if values["attempts"] > 0]
    readiness = round(sum(float(v["score"]) for v in measured) / len(measured)) if measured else 0
    strongest = max(mastery, key=lambda skill: float(mastery[skill]["score"]))
    weakest = min(
        mastery,
        key=lambda skill: (float(mastery[skill]["score"]), int(mastery[skill]["attempts"])),
    )
    return {"readiness": readiness, "strongest": strongest, "weakest": weakest}


__all__ = [
    "SKILL_LABELS", "TRACK_LABELS", "build_practice_queue", "diagnostic_question_ids",
    "get_mastery", "get_question", "questions_for_track", "readiness_summary",
]
