import unittest
from collections import Counter

from engine import (
    SKILL_LABELS,
    build_practice_queue,
    diagnostic_question_ids,
    get_mastery,
    get_question,
    questions_for_track,
)


class EngineTests(unittest.TestCase):
    def test_each_track_has_exactly_one_hundred_questions(self):
        for track in SKILL_LABELS:
            self.assertEqual(len(questions_for_track(track)), 100)

    def test_each_track_has_ten_skills_and_twenty_diagnostic_questions(self):
        for track, skills in SKILL_LABELS.items():
            self.assertEqual(len(skills), 10)
            self.assertEqual(len(diagnostic_question_ids(track)), 20)
            counts = Counter(q["skill"] for q in questions_for_track(track))
            self.assertTrue(all(counts[skill] == 10 for skill in skills))

    def test_wrong_question_remains_eligible(self):
        question = questions_for_track("data")[0]
        attempts = [{
            "question_id": question["id"], "skill": question["skill"],
            "correct": 0, "confidence": "Certain",
        }]
        queue = build_practice_queue("data", attempts, get_mastery(attempts, "data"), count=100)
        self.assertIn(question["id"], queue)

    def test_correct_question_is_permanently_excluded(self):
        question = questions_for_track("engineering")[0]
        attempts = [
            {"question_id": question["id"], "skill": question["skill"], "correct": 0, "confidence": "Certain"},
            {"question_id": question["id"], "skill": question["skill"], "correct": 1, "confidence": "Certain"},
        ]
        queue = build_practice_queue("engineering", attempts, get_mastery(attempts, "engineering"), count=100)
        self.assertNotIn(question["id"], queue)

    def test_diagnostic_weakness_is_prioritized(self):
        track = "finance"
        weak_skill = next(iter(SKILL_LABELS[track]))
        attempts = []
        for question_id in diagnostic_question_ids(track):
            question = get_question(question_id)
            attempts.append({
                "question_id": question_id,
                "skill": question["skill"],
                "correct": 0 if question["skill"] == weak_skill else 1,
                "confidence": "Certain",
            })
        queue = build_practice_queue(track, attempts, get_mastery(attempts, track), count=10)
        self.assertEqual(get_question(queue[0])["skill"], weak_skill)
        self.assertTrue(any(get_question(qid)["skill"] == weak_skill for qid in queue[:5]))


if __name__ == "__main__":
    unittest.main()
