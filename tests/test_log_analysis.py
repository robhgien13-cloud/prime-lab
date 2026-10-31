import unittest
from src.prime_lab.log_analysis import analyze

class LogAnalysisTests(unittest.TestCase):
    def test_known_prime_count(self):
        d = analyze(1000)
        self.assertEqual(d["prime_count"], 168)
        self.assertEqual(d["prime_count_comparison"][-1]["actual"], 168)
    def test_gap_normalization(self):
        d = analyze(100)
        self.assertEqual(d["gap_over_ln_prime"]["count"], 24)
        self.assertGreater(d["gap_over_ln_prime"]["mean"], 0)
    def test_reject_invalid_limit(self):
        with self.assertRaises(ValueError):
            analyze(0)
if __name__ == "__main__":
    unittest.main()
