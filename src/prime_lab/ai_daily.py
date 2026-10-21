"""Archive validated AI conjectures, refusing duplicates; no fabricated ten-count."""
import json
from datetime import datetime,timezone
from pathlib import Path
from .ai_batch import propose_batch
from .llm_structured import experiment_candidate
from .pipeline import run as rebuild

def run(day=None,root=Path("."),candidates=None):
    day=day or datetime.now(timezone.utc).date().isoformat()
    if datetime.strptime(day,"%Y-%m-%d").strftime("%Y-%m-%d")!=day: raise ValueError("Invalid day")
    folder=root/"data"/"runs"/day
    folder.mkdir(parents=True,exist_ok=True)
    known=set()
    for p in (root/"data"/"runs").glob("*/*.json"):
        item=json.loads(p.read_text(encoding="utf-8"))
        spec=item.get("experiment",{}).get("spec")
        if spec: known.add(json.dumps(spec,sort_keys=True))
    batch=propose_batch() if candidates is None else candidates
    made=0
    next_id=1
    for candidate in batch:
        if made>=10: break
        spec=candidate["spec"]
        fingerprint=json.dumps(spec,sort_keys=True)
        if fingerprint in known: continue
        rid="AI-"+day.replace("-","")+"-"+str(next_id).zfill(2)
        path=folder/(rid+".json")
        while path.exists():
            next_id+=1
            rid="AI-"+day.replace("-","")+"-"+str(next_id).zfill(2)
            path=folder/(rid+".json")
        checked=experiment_candidate(candidate)
        finite=checked["finite_check"]
        record={
            "schema_version":"1.0","run_id":rid,"date":day,
            "title":f"AI研究仮説 {made+1:02d}（未査読）",
            "status":finite["status"],
            "summary":finite["beginner_explanation"],
            "hypothesis":finite["statement"],
            "hypothesis_origin":"LLM structured candidate (unverified)",
            "plain_language":checked["plain_language"],
            "experiment":{"spec":spec,"result":finite},
            "motivation":candidate["motivation"],
            "proof":"なし","prior_art":"未照合",
            "novelty_status":"過去の同一条件なし・学術的新規性は未確認",
            "provenance":{"generator":"Gemini API batch","llm_used":True},
        }
        record["plain_language"]["limits"]+=" 過去の完全一致はありませんが、学術的新規性は確認していません。"
        with path.open("x",encoding="utf-8") as f:
            json.dump(record,f,ensure_ascii=False,indent=2)
            f.write("\n")
        known.add(fingerprint)
        made+=1
        next_id+=1
    rebuild(day,root,create_templates=False)
    print(f"AI proposals archived: {made}/10; duplicates/invalid proposals are not replaced")
    return made

if __name__=="__main__": run()
