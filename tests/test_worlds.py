import tempfile
import unittest
from pathlib import Path
from src.prime_lab.worlds import primes_through, explore, run

class WorldResearchTests(unittest.TestCase):
    def test_primes(self):
        self.assertEqual(primes_through(13), [2, 3, 5, 7, 11, 13])

    def test_mapping_and_operations(self):
        result = explore(limit=100, sample=8)
        self.assertEqual(result["sample_pairs"][0], {"integer_index": 1, "prime_value": 2})
        self.assertEqual(result["sample_pairs"][2]["prime_value"], 5)
        self.assertEqual(result["candidate_transport_operations"][0]["prime_world_sum_candidate"], 3)
        self.assertEqual(result["candidate_transport_operations"][0]["ordinary_sum_of_prime_values"], 4)
        self.assertEqual(len(result["prediction_baseline"]["absolute_errors"]), 4)

    def test_run_writes_separate_research_data(self):
        with tempfile.TemporaryDirectory() as d:
            path = run(Path(d), day="2026-10-31", limit=100, sample=8)
            self.assertTrue(path.is_file())
            self.assertIn("model_status", path.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
