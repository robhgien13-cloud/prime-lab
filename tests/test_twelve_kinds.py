import json
import unittest
from src.prime_lab.structured import verify
from src.prime_lab.llm_structured import parse_candidate

class TwelveKindsTests(unittest.TestCase):
    def test_all_new_kinds(self):
        for kind in ("cousin_prime_count_window", "sexy_prime_count_window",
                     "prime_triplet_count_window", "small_gap_count_window"):
            with self.subTest(kind=kind):
                spec = {"kind":kind, "limit":100, "window":10, "threshold":1}
                self.assertIn("status", verify(spec))
                self.assertEqual(parse_candidate(json.dumps({**spec,"motivation":"調査する"}))["spec"], spec)
    def test_known_counts(self):
        self.assertEqual(verify({"kind":"cousin_prime_count_window","limit":100,"window":10,"threshold":1})["counterexample"]["number"], 20)
        self.assertEqual(verify({"kind":"small_gap_count_window","limit":100,"window":10,"threshold":0})["counterexample"]["number"], 2)
    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            verify({"kind":"prime_triplet_count_window","limit":100,"window":200,"threshold":1})
if __name__ == "__main__":
    unittest.main()
