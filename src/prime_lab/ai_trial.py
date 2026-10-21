"""Run one optional LLM candidate and archive it without claiming proof."""
import json
from datetime import datetime, timezone
from pathlib import Path
from .gemini_free import propose
from .llm_structured import experiment_candidate
from .pipeline import run as refresh

def run(day=None, root=Path("."), candidate=None):
    day = day or datetime.now(timezone.utc).date().isoformat()
    datetime.strptime(day, "%Y-%m-%d")
    candidate = propose() if candidate is None else candidate
    spec = candidate["spec"]
    existing = []
    for previous in sorted((root / "data" / "runs").glob("*/*.json")):
        old = json.loads(previous.read_text(encoding="utf-8"))
        if old.get("experiment", {}).get("spec", {}) == spec:
            existing.append(old.get("run_id", previous.stem))
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
        "summary":("既出の条件です。 " if existing else "") + finite["beginner_explanation"],
        "hypothesis":finite["statement"],
        "hypothesis_origin":"LLM structured candidate (unverified)",
        "plain_language":result["plain_language"],
        "experiment":{"spec":candidate["spec"],"result":finite},
        "proof":"なし","prior_art":"未照合",
        "duplicate_of":existing,
        "novelty_status":"既存の実験と同一" if existing else "既存の実験とは異なる・学術的新規性未確認",
        "provenance":{"llm_used":True,"generator":"LLM"},
    }
    entry["plain_language"]["limits"] += (
        " 既存の同一条件：" + ", ".join(existing) + "。"
        if existing else " 過去の記録と完全一致しませんが、学術的な新規性は未確認です。"
    )
    with path.open("x", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
        f.write("\n")
    refresh(day, root, create_templates=False)
    return path

if __name__ == "__main__":
    print(run())
