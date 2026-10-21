import json
import tempfile
import unittest
from pathlib import Path
from src.prime_lab.ai_daily import run

class DailyAITests(unittest.TestCase):
    def test_batch_archives_distinct_candidates(self):
        def candidate(modulus,residues):
            return {"spec":{"kind":"prime_residue","limit":100,"modulus":modulus,"residues":residues},"motivation":"調査する","origin":"LLM proposal (unverified)"}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            batch=[candidate(6,[1,5]),candidate(6,[1,5]),candidate(5,[1,2,3,4])]
            self.assertEqual(run("2026-10-21",root,batch),2)
            self.assertEqual(run("2026-10-21",root,batch),0)
            public=json.loads((root/"data"/"research.json").read_text(encoding="utf-8"))
            self.assertEqual(len(public["records"]),2)
if __name__=="__main__":unittest.main()
