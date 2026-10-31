import unittest
from src.prime_lab.structured import verify, validate
from src.prime_lab.llm_structured import parse_candidate
import json

class ExpandedKindsTests(unittest.TestCase):
    def test_twin_pairs(self):
        result = verify({"kind":"twin_prime_count_window","limit":100,"window":10,"threshold":1})
        self.assertEqual(result["counterexample"]["number"], 8)
    def test_upper_count(self):
        result = verify({"kind":"prime_count_window_at_most","limit":100,"window":10,"threshold":2})
        self.assertEqual(result["counterexample"]["number"], 2)
    def test_gap_lower_bound(self):
        result = verify({"kind":"prime_gap_lower_bound","limit":100,"window":3,"threshold":4})
        self.assertEqual(result["counterexample"]["number"], 3)
    def test_parse_new_kind(self):
        c = parse_candidate(json.dumps({"kind":"twin_prime_count_window","limit":100,"window":10,"threshold":1,"motivation":"区間内の双子素数を調べる"}))
        self.assertEqual(c["spec"]["kind"], "twin_prime_count_window")
    def test_reject_empty_windows(self):
        with self.assertRaises(ValueError):
            validate({"kind":"twin_prime_count_window","limit":100,"window":500,"threshold":1})
if __name__=="__main__":
    unittest.main()
