import tempfile
import unittest
from pathlib import Path
from src.prime_lab.pipeline import record, run

class PipelineTests(unittest.TestCase):
    def test_refutation(self):
        r = record(2, "2026-10-21", 100)
        self.assertIsNotNone(r["counterexample"])
        self.assertIn("反例発見", r["status"])
        self.assertFalse(r["provenance"]["llm_used"])
    def test_full_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            records=run("2026-10-21", root, 100)
            self.assertEqual(len(records),10)
            self.assertEqual(len(run("2026-10-21", root, 100)),10)
            self.assertEqual(len(list((root/"data"/"runs"/"2026-10-21").glob("T-*.json"))),10)
            self.assertTrue((root/"data"/"research.json").exists())
if __name__=="__main__":
    unittest.main()
