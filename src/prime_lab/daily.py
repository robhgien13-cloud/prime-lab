"""Ten daily reproducible finite checks, without API calls or discovery claims."""
import json
from datetime import datetime, timezone
from pathlib import Path
from .structured import verify
from .pipeline import run as rebuild

def specs(day):
    seed=int(day.replace("-",""))
    mods=[3,4,5,6,7,8,9,10,11,12]
    output=[]
    for i,m in enumerate(mods):
        kind="prime_gap_divisible" if i%3==0 else "prime_residue"
        residues=sorted({(seed//(i+1)+i)%m, (seed//(i+2)+i+1)%m})
        output.append({"kind":kind,"limit":1000,"modulus":m,"residues":residues})
    return output

def run(day=None,root=Path(".")):
    day=day or datetime.now(timezone.utc).date().isoformat()
    if datetime.strptime(day,"%Y-%m-%d").strftime("%Y-%m-%d")!=day:
        raise ValueError("Invalid date")
    folder=root/"data"/"runs"/day
    folder.mkdir(parents=True,exist_ok=True)
    existing_specs={}
    for path in (root/"data"/"runs").glob("*/*.json"):
        item=json.loads(path.read_text(encoding="utf-8"))
        spec=item.get("experiment",{}).get("spec")
        if spec:
            existing_specs.setdefault(json.dumps(spec,sort_keys=True),[]).append(item.get("run_id",path.stem))
    made=0
    for i,spec in enumerate(specs(day),1):
        rid=f"D-{day.replace('-','')}-{i:02d}"
        path=folder/(rid+".json")
        if path.exists():
            continue
        result=verify(spec)
        matches=existing_specs.get(json.dumps(spec,sort_keys=True),[])
        record={
            "schema_version":"1.0","run_id":rid,"date":day,
            "title":f"定期有限検証 {i:02d}",
            "theme_class":"B" if spec["kind"]=="prime_gap_divisible" else "C",
            "status":result["status"],
            "summary":result["beginner_explanation"],
            "hypothesis":result["statement"],
            "hypothesis_origin":"日付に基づく自動生成条件（AIの仮説ではない）",
            "plain_language":{
                "question":result["statement"]+"という条件は成り立つ？",
                "background":"素数は1と自分自身以外で割り切れない2以上の整数です。",
                "method":"1000以下を有限計算で検査しました。",
                "finding":result["beginner_explanation"],
                "limits":"有限検査は証明ではありません。新規性は未確認です。"+(" 過去と同一条件あり。" if matches else ""),
                "next_question":"この条件が成り立つ理由、または反例の一般化を検討します。"
            },
            "experiment":{"spec":spec,"result":result},
            "duplicate_of":matches,
            "proof":"なし","prior_art":"未照合",
            "provenance":{"generator":"deterministic daily generator","llm_used":False}
        }
        with path.open("x",encoding="utf-8") as f:
            json.dump(record,f,ensure_ascii=False,indent=2)
            f.write("\n")
        made+=1
        existing_specs.setdefault(json.dumps(spec,sort_keys=True),[]).append(rid)
    rebuild(day,root,create_templates=False)
    print(f"Daily checks created: {made}; total daily checks: 10")
    return made

if __name__=="__main__":
    run()
