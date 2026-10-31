import json
import tempfile
import unittest
from pathlib import Path
from src.prime_lab.research_feedback import summarize, prompt_context

class ResearchFeedbackTests(unittest.TestCase):
    def test_empty_history(self):
        with tempfile.TemporaryDirectory() as d:
            result = summarize(Path(d))
            self.assertEqual(result["distinct_conditions_reviewed"], 0)
            self.assertEqual(len(result["goals"]), 4)
            self.assertIn("予測", prompt_context(Path(d)))

    def test_deduplicates_different_limits(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "data" / "runs" / "2026-10-30"
            folder.mkdir(parents=True)
            for i, limit in enumerate((100, 1000)):
                (folder / f"{i}.json").write_text(json.dumps({
                    "status": "有限範囲で反例なし",
                    "experiment": {"spec": {"kind": "prime_residue",
                                            "limit": limit, "modulus": 6,
                                            "residues": [1, 5]}}
                }), encoding="utf-8")
            self.assertEqual(summarize(Path(d))["distinct_conditions_reviewed"], 1)

if __name__ == "__main__":
    unittest.main()
