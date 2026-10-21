import tempfile
import unittest
from pathlib import Path
from src.prime_lab.engine import prime,run
class Tests(unittest.TestCase):
    def test_prime(self):
        self.assertEqual([n for n in range(30) if prime(n)],[2,3,5,7,11,13,17,19,23,29])
    def test_ten_records(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.assertEqual(len(run("2026-10-21",root)),10)
            self.assertEqual(len(run("2026-10-21",root)),10)
            self.assertEqual(len(list((root/"data"/"runs").glob("*/*.json"))),10)
if __name__=="__main__": unittest.main()
