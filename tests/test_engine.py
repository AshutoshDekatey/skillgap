import unittest

from engine import SKILL_LABELS, build_practice_queue, diagnostic_question_ids, get_mastery


class EngineTests(unittest.TestCase):
    def test_each_track_has_twelve_diagnostic_questions(self):
        for track in SKILL_LABELS:
            self.assertEqual(len(diagnostic_question_ids(track)), 12)

    def test_each_track_has_six_skills(self):
        self.assertTrue(all(len(skills) == 6 for skills in SKILL_LABELS.values()))

    def test_tracks_remain_separate(self):
        attempts = [{"question_id": 1, "skill": "pd_inspect", "correct": 1, "confidence": "Certain"}]
        pandas_mastery = get_mastery(attempts, "pandas")
        terraform_mastery = get_mastery([], "terraform")
        self.assertGreater(pandas_mastery["pd_inspect"]["score"], 0)
        self.assertTrue(all(value["score"] == 0 for value in terraform_mastery.values()))

    def test_practice_queue_has_five_questions(self):
        mastery = get_mastery([], "capital_markets")
        queue = build_practice_queue("capital_markets", [], mastery, count=5)
        self.assertEqual(len(queue), 5)
        self.assertTrue(all(question_id >= 201 for question_id in queue))


if __name__ == "__main__":
    unittest.main()
