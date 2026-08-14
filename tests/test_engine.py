import unittest

from engine import build_practice_queue, diagnostic_question_ids, get_mastery


class EngineTests(unittest.TestCase):
    def test_diagnostic_has_two_questions_per_skill(self):
        self.assertEqual(len(diagnostic_question_ids()), 16)

    def test_unattempted_skills_start_unmeasured(self):
        mastery = get_mastery([])
        self.assertTrue(all(values["score"] == 0 for values in mastery.values()))
        self.assertTrue(all(values["attempts"] == 0 for values in mastery.values()))

    def test_weak_skill_is_prioritized(self):
        attempts = []
        representative_questions = {
            "inspection": 1,
            "missing": 5,
            "duplicates": 9,
            "types": 13,
            "text": 17,
            "filtering": 21,
            "outliers": 25,
            "joins": 29,
        }
        for skill, question_id in representative_questions.items():
            attempts.append(
                {
                    "question_id": question_id,
                    "skill": skill,
                    "correct": 0 if skill == "missing" else 1,
                    "confidence": "Certain",
                }
            )
        mastery = get_mastery(attempts)
        queue = build_practice_queue(attempts, mastery, count=5)
        self.assertTrue(any(question_id in queue for question_id in [6, 7, 8]))


if __name__ == "__main__":
    unittest.main()
