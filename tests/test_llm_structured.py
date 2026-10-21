import json
import unittest
from src.prime_lab.llm_structured import parse_candidate,experiment_candidate

class LLMStructuredTests(unittest.TestCase):
    def test_candidate(self):
        raw=json.dumps({"kind":"prime_residue","limit":100,"modulus":6,"residues":[1,5],"motivation":"余りの規則性を調べたい"})
        candidate=parse_candidate(raw)
        result=experiment_candidate(candidate)
        self.assertFalse(result["ai_hypothesis_verified"])
        self.assertEqual(result["model_text_matches_spec"],"未確認")
        self.assertIsNone(result["finite_check"]["counterexample"])
    def test_reject_code(self):
        raw=json.dumps({"kind":"prime_residue","limit":100,"modulus":6,"residues":[1,5],"motivation":"a","python":"print(1)"})
        with self.assertRaises(ValueError):parse_candidate(raw)
    def test_reject_bad_modulus(self):
        raw=json.dumps({"kind":"prime_residue","limit":100,"modulus":0,"residues":[1],"motivation":"a"})
        with self.assertRaises(ValueError):parse_candidate(raw)
if __name__=="__main__":
    unittest.main()
