import unittest
from src.prime_lab.structured import validate, verify

class StructuredTests(unittest.TestCase):
    def test_supported(self):
        x = verify({"kind":"prime_residue","limit":100,"modulus":6,"residues":[1,5]})
        self.assertIsNone(x["counterexample"])
        self.assertFalse(x["mathematically_proven"])
    def test_refutation(self):
        x = verify({"kind":"prime_residue","limit":100,"modulus":6,"residues":[1]})
        self.assertIsNotNone(x["counterexample"])
        self.assertEqual(x["status"],"有限範囲で反例発見")
    def test_reject_unsafe(self):
        cases = [
            {"kind":"prime_residue","limit":True,"modulus":6,"residues":[1,5]},
            {"kind":"prime_residue","limit":100000,"modulus":6,"residues":[1,5]},
            {"kind":"prime_residue","limit":100,"modulus":6,"residues":[1,1]},
            {"kind":"prime_residue","limit":100,"modulus":6,"residues":[1,5],"code":"print(1)"},
        ]
        for x in cases:
            with self.assertRaises(ValueError): validate(x)

if __name__=="__main__":
    unittest.main()
