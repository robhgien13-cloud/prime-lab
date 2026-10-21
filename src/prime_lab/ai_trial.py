"""Run one optional LLM candidate and archive it without claiming proof."""
import json
from datetime import datetime, timezone
from pathlib import Path
from .llm_structured import propose, experiment_candidate
from .pipeline import run as refresh

def run(day=None, root=Path("."), candidate=None):
    day = day or datetime.now(timezone.utc).date().isoformat()
    datetime.strptime(day, "%Y-%m-%d")
    candidate = propose() if candidate is None else candidate
    result = experiment_candidate(candidate)
    folder = root / "data" / "runs" / day
    folder.mkdir(parents=True, exist_ok=True)
    rid = "AI-" + day.replace("-", "") + "-01"
    path = folder / (rid + ".json")
    if path.exists():
        raise FileExistsError("AI trial already exists for this date")
    finite = result["finite_check"]
    entry = {
        "schema_version":"1.0", "run_id":rid, "date":day,
        "title":"AIの仮説候補を数値検証（未査読）",
        "status":finite["status"]+"／AI説明との一致未確認",
        "summary":finite["beginner_explanation"],
        "hypothesis":finite["statement"],
        "hypothesis_origin":"LLM structured candidate (unverified)",
        "plain_language":result["plain_language"],
        "experiment":{"spec":candidate["spec"],"result":finite},
        "proof":"なし","prior_art":"未照合",
        "provenance":{"llm_used":True,"generator":"LLM"},
    }
    with path.open("x", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
        f.write("\n")
    refresh(day, root)
    return path

if __name__ == "__main__":
    print(run())
