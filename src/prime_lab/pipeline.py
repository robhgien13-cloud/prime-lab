"""End-to-end trial: structured hypothesis -> finite verification -> readable report.

No LLM API is invoked. Generated proposals are deterministic demonstration
inputs, not novel AI research or independently verified discoveries.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from .structured import verify

TEMPLATES = [
    {"kind":"prime_residue","modulus":6,"residues":[1,5]},
    {"kind":"prime_residue","modulus":6,"residues":[1]},
    {"kind":"prime_gap_divisible","modulus":2,"residues":[0]},
    {"kind":"prime_last_digit","modulus":10,"residues":[1,3,7,9]},
    {"kind":"prime_residue","modulus":5,"residues":[1,2,3,4]},
    {"kind":"prime_gap_divisible","modulus":4,"residues":[0,2]},
    {"kind":"prime_residue","modulus":7,"residues":[1,2,3,4,5,6]},
    {"kind":"prime_residue","modulus":7,"residues":[1,2,3]},
    {"kind":"prime_gap_divisible","modulus":6,"residues":[0,2,4]},
    {"kind":"prime_residue","modulus":10,"residues":[1,3,7,9]},
]

def record(i, day, limit=1000):
    if type(i) is not int or not 1 <= i <= len(TEMPLATES):
        raise ValueError("index must be between 1 and 10")
    template = dict(TEMPLATES[i-1], limit=limit)
    result = verify(template)
    rid = "T-" + day.replace("-", "") + "-" + f"{i:02d}"
    counterexample = result["counterexample"]
    finding = result["beginner_explanation"]
    return {
        "schema_version": "1.0",
        "run_id": rid, "date": day, "title": f"素数の予想を確かめる {i:02d}",
        "theme_class": "C" if "gap" not in template["kind"] else "B",
        "status": result["status"], "summary": finding,
        "hypothesis": result["statement"],
        "hypothesis_origin": "事前登録された試験用テンプレート（AIによる新規提案ではない）",
        "plain_language": {
            "question": result["statement"] + "という予想は正しい？",
            "background": "素数は1と自分自身以外で割り切れない2以上の整数です。余りは割り算で残る数です。",
            "method": f"{limit}以下の対象について、1つずつ余りを調べました。",
            "finding": finding,
            "limits": "有限個の計算は、すべての整数についての証明にはなりません。",
            "next_question": "なぜこの余りが現れるのか、数式で説明できるでしょうか？",
        },
        "experiment": {"spec": template, "result": result, "code": "src/prime_lab/structured.py"},
        "counterexample": counterexample, "proof": "なし",
        "prior_art": "未照合",
        "provenance": {"generator": "deterministic test templates", "llm_used": False},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

def run(day, root=Path("."), limit=1000, create_templates=True):
    folder = root / "data" / "runs" / day
    folder.mkdir(parents=True, exist_ok=True)
    if create_templates:
        for i in range(1, 11):
            entry = record(i, day, limit)
            path = folder / (entry["run_id"] + ".json")
            if not path.exists():
                path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    all_records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "data" / "runs").glob("*/*.json"))]
    public_records = [r for r in all_records if not r.get("run_id", "").startswith(("T-", "D-"))]
    ids = [r["run_id"] for r in all_records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate research IDs")
    refuted = sum("反例発見" in r.get("status", "") for r in public_records)
    hypotheses = sum(r.get("provenance", {}).get("llm_used", False) for r in public_records)
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "cycles": len(public_records), "hypotheses": hypotheses, "refuted": refuted, "verified": 0,
        "records": [{
            "id": r["run_id"], "date": r["date"], "title": r["title"],
            "status": r["status"], "summary": r["summary"],
            "plain_language": r.get("plain_language", {}),
            "origin": r.get("hypothesis_origin", "不明"),
        } for r in public_records],
    }
    (root / "data" / "research.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return all_records

if __name__ == "__main__":
    import os
    date = os.getenv("PRIME_LAB_DATE") or datetime.now(timezone.utc).date().isoformat()
    print("Archived:", len(run(date)))
