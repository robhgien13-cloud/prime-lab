import json
import tempfile
import unittest
from pathlib import Path
from src.prime_lab.literature import search, annotate_recent

class LiteratureTests(unittest.TestCase):
    def test_sources_and_no_false_novelty(self):
        def fake(url):
            if "oeis.org" in url:
                return json.dumps({"results":[{"number":40,"name":"Prime gaps"}]}).encode()
            return b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/1234.5678</id><title>Prime intervals</title></entry></feed>'
        record={"experiment":{"spec":{"kind":"prime_gap_bound"}}}
        result=search(record, fetch=fake)
        self.assertFalse(result["novelty_confirmed"])
        self.assertEqual(result["sources"]["oeis"]["hits"][0]["id"], "A000040")
        self.assertEqual(result["sources"]["arxiv"]["state"], "検索済み")
        self.assertIn("未実装", result["sources"]["zbmath"]["state"])

    def test_archive_separate_and_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            folder=root/"data"/"runs"/"2026-10-21"
            folder.mkdir(parents=True)
            record={"run_id":"AI-20261021-01","provenance":{"llm_used":True},"status":"有限範囲で反例なし","experiment":{"spec":{"kind":"prime_gap_bound"}}}
            (folder/"AI-20261021-01.json").write_text(json.dumps(record),encoding="utf-8")
            def fake(url):
                return b'{"results":[]}' if "oeis.org" in url else b'<feed xmlns="http://www.w3.org/2005/Atom"/>'
            self.assertEqual(len(annotate_recent(root, fetch=fake)),1)
            self.assertEqual(len(annotate_recent(root, fetch=fake)),0)
            self.assertTrue((root/"data"/"literature"/"AI-20261021-01.json").exists())

if __name__ == "__main__":
    unittest.main()
