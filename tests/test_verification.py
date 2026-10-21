import unittest
from src.prime_lab.verification import check, validate_spec

class VerificationTests(unittest.TestCase):
    def test_valid(self):
        for kind in ("prime_mod_6", "twin_prime_gap", "goldbach_even"):
            result = check({"kind":kind, "limit":100})
            self.assertIsNone(result["counterexample"])
            self.assertFalse(result["proof"])
            self.assertGreater(result["tested_cases"],0)
    def test_invalid(self):
        for spec in ({"kind":"__import__", "limit":100}, {"kind":"prime_mod_6","limit":1000000}, {"kind":"prime_mod_6","limit":True}, {"kind":"prime_mod_6","limit":100,"code":"print(1)"}):
            with self.assertRaises(ValueError): validate_spec(spec)
if __name__ == "__main__":
    unittest.main()
