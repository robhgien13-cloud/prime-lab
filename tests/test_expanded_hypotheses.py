import unittest
from src.prime_lab.structured import verify, validate
from src.prime_lab.llm_structured import parse_candidate
import json

class ExpandedHypothesesTests(unittest.TestCase):
    def test_gap_bound_counterexample(self):
        result = verify({"kind":"prime_gap_bound","limit":100,"window":2,"threshold":2})
        self.assertEqual(result["status"], "有限範囲で反例発見")
        self.assertEqual(result["counterexample"]["number"], 7)
    def test_interval_count_counterexample(self):
        result = verify({"kind":"prime_count_window","limit":100,"window":3,"threshold":2})
        self.assertEqual(result["status"], "有限範囲で反例発見")
        self.assertEqual(result["counterexample"]["number"], 4)
    def test_parse_expanded(self):
        raw=json.dumps({"kind":"prime_gap_bound","limit":100,"window":2,"threshold":2,"motivation":"素数間隔を調査"})
        self.assertEqual(parse_candidate(raw)["spec"]["kind"],"prime_gap_bound")
    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            validate({"kind":"prime_count_window","limit":100,"window":0,"threshold":2})
if __name__=="__main__": unittest.main()
