from __future__ import annotations

from collections import defaultdict

from questions import QUESTIONS


SKILL_LABELS = {
    "inspection": "Inspecting data",
    "missing": "Missing values",
    "duplicates": "Duplicates",
    "types": "Data types",
    "text": "Text cleaning",
    "filtering": "Filtering & replacement",
    "outliers": "Outliers",
    "joins": "Joins & reshaping",
}


def get_question(question_id: int) -> dict:
    return next(question for question in QUESTIONS if question["id"] == question_id)


def diagnostic_question_ids() -> list[int]:
    """Use two fixed, medium-coverage questions from every skill."""
    selected: list[int] = []
    counts: defaultdict[str, int] = defaultdict(int)
    for question in QUESTIONS:
        skill = question["skill"]
        if counts[skill] < 2:
            selected.append(question["id"])
            counts[skill] += 1
    return selected


def get_mastery(attempts: list[dict]) -> dict[str, dict[str, float | int]]:
    """
    Return an explainable mastery estimate.

    Correctness contributes most. Confidence adjusts the score slightly:
    confident mistakes reduce mastery more than admitted guesses, while
    confident correct answers add a small positive signal. Repeated practice
    gradually outweighs the neutral prior.
    """
    grouped: defaultdict[str, list[dict]] = defaultdict(list)
    for attempt in attempts:
        grouped[attempt["skill"]].append(attempt)

    confidence_weight = {
        "Guessing": 0.85,
        "Unsure": 0.95,
        "Fairly sure": 1.0,
        "Certain": 1.08,
    }
    mastery: dict[str, dict[str, float | int]] = {}
    for skill in SKILL_LABELS:
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

        # One neutral prior observation prevents extreme 0/100 scores after one answer.
        score = ((earned + 0.5) / (possible + 1.0)) * 100
        mastery[skill] = {
            "score": round(score, 1),
            "attempts": len(skill_attempts),
        }
    return mastery


def build_practice_queue(
    attempts: list[dict], mastery: dict[str, dict[str, float | int]], count: int = 10
) -> list[int]:
    if not attempts:
        return []

    attempt_count: defaultdict[int, int] = defaultdict(int)
    for attempt in attempts:
        attempt_count[attempt["question_id"]] += 1

    def priority(question: dict) -> tuple[float, int, int]:
        skill_score = float(mastery[question["skill"]]["score"])
        seen = attempt_count[question["id"]]
        # Weak skills come first; unseen items beat repeated ones within a skill.
        return (skill_score + seen * 18, seen, question["difficulty"])

    return [question["id"] for question in sorted(QUESTIONS, key=priority)[:count]]


def readiness_summary(mastery: dict[str, dict[str, float | int]]) -> dict:
    measured = [values for values in mastery.values() if values["attempts"] > 0]
    readiness = round(sum(float(v["score"]) for v in measured) / len(measured)) if measured else 0
    strongest = max(mastery, key=lambda skill: float(mastery[skill]["score"]))
    weakest = min(
        mastery,
        key=lambda skill: (
            float(mastery[skill]["score"]),
            int(mastery[skill]["attempts"]),
        ),
    )
    return {"readiness": readiness, "strongest": strongest, "weakest": weakest}
