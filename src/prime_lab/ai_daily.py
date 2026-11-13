"""Archive validated AI conjectures, refusing duplicates; no fabricated ten-count."""
import json
from datetime import datetime,timezone
from pathlib import Path
from .ai_batch import propose_batch
from .inspiration import pick_random
from .research_feedback import prompt_context, reference_for_experiment
from .llm_structured import experiment_candidate
from .pipeline import run as rebuild

def run(day=None,root=Path("."),candidates=None):
    day=day or datetime.now(timezone.utc).date().isoformat()
    if datetime.strptime(day,"%Y-%m-%d").strftime("%Y-%m-%d")!=day: raise ValueError("Invalid day")
    folder=root/"data"/"runs"/day
    folder.mkdir(parents=True,exist_ok=True)
    known=set()
    prior_records=[]
    for p in (root/"data"/"runs").glob("*/*.json"):
        item=json.loads(p.read_text(encoding="utf-8"))
        spec=item.get("experiment",{}).get("spec")
        if spec:
            known.add(json.dumps(spec,sort_keys=True))
            prior_records.append(item)
    words=pick_random()
    batch=propose_batch(inspiration=words, research_context=prompt_context(root)) if candidates is None else candidates
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
        # Link to a real earlier experiment in the same verification family.
        related=[x for x in prior_records if x.get('experiment',{}).get('spec',{}).get('kind')==spec.get('kind')]
        parent=max(related,key=lambda x:(str(x.get('date','')),str(x.get('run_id','')))) if related else None
        if parent:
            prev_spec=parent['experiment']['spec']
            changed=[k for k in spec if prev_spec.get(k)!=spec[k]]
            rationale=('前回の「'+str(parent.get('hypothesis',''))+'」は「'+str(parent.get('status','不明'))+'」でした。'
                       +'今回は同じ種類の条件について、'+('・'.join(changed) if changed else '条件')+'を変えて再検証します。'
                       +'これは条件の比較であり、AIの内部思考を再現したものではありません。')
        else:
            rationale='同じ種類の先行実験記録がないため、新しい検証系列として開始します。AIの内部思考を再現したものではありません。'
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
            "research_basis":reference_for_experiment(spec, candidate["motivation"]),
            "research_progression":{"previous_run_id":parent.get("run_id") if parent else None,
                "previous_result":parent.get("status") if parent else None,
                "next_question":checked["plain_language"].get("next_question"),
                "selection_reason":rationale,
                "link_type":"same_kind_comparison" if parent else "new_series",
                "note":"関連する先行実験との比較。因果関係やAIの内部推論を証明するものではありません。"},
            "research_direction":"予測・生成と分布・構造の規則性を探索",
            "inspiration":words,
            "proof":"なし","prior_art":"未照合",
            "novelty_status":"過去の同一条件なし・学術的新規性は未確認",
            "provenance":{"generator":"Gemini API batch","llm_used":True},
        }
        record["plain_language"]["limits"]+=" 過去の完全一致はありませんが、学術的新規性は確認していません。"
        with path.open("x",encoding="utf-8") as f:
            json.dump(record,f,ensure_ascii=False,indent=2)
            f.write("\n")
        known.add(fingerprint)
        prior_records.append(record)
        made+=1
        next_id+=1
    rebuild(day,root,create_templates=False)
    print(f"AI proposals archived: {made}/10; duplicates/invalid proposals are not replaced")
    return made

if __name__=="__main__": run()
