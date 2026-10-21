import json
import math
from datetime import datetime, timezone
from pathlib import Path

def prime(n):
    return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))

def experiment(i, day, limit=1000):
    primes = [n for n in range(2, limit + 1) if prime(n)]
    gaps = [b-a for a,b in zip(primes, primes[1:])]
    names = ["素数の分布","素数間の距離","剰余と合同式","特殊な形の素数","素数同士の関係","素数判定","情報理論との比較","素数の末尾"]
    mode = (i-1)%8
    if mode == 0: result = f"{limit}以下の素数は{len(primes)}個でした。"
    elif mode == 1: result = f"隣接素数の差の最大値は{max(gaps)}でした。"
    elif mode == 2: result = f"3より大きい素数の6で割った余りは{sorted({p%6 for p in primes if p>3})}でした。"
    elif mode == 3: result = f"2^n-1（n=2～10）で素数のものは{[2**n-1 for n in range(2,11) if prime(2**n-1)]}でした。"
    elif mode == 4:
        nums = range(4, min(100,limit)+1, 2)
        result = f"4から{min(100,limit)}までの偶数{len(list(nums))}個を、2素数の和で表せることを数値確認しました。"
    elif mode == 5: result = f"試し割り法で{limit}以下の素数を列挙しました。"
    elif mode == 6:
        counts = [gaps.count(g) for g in set(gaps)]
        entropy = -sum((c/len(gaps))*math.log2(c/len(gaps)) for c in counts)
        result = f"素数間隔の経験的情報量は{entropy:.3f}ビットでした。"
    else: result = f"5より大きい素数の末尾の頻度は{ {d:sum(p%10==d for p in primes if p>5) for d in (1,3,7,9)} }でした。"
    return {"schema_version":"1.0","run_id":f"R-{day.replace('-','')}-{i:02d}","date":day,"theme_class":"ABCDEFGH"[mode],"title":names[mode],"status":"数値実験（新発見ではない）","summary":result,"hypothesis":"新規仮説は未生成","plain_language":{"question":names[mode]+"について何がわかる？","background":"素数は1と自分自身でしか割り切れない2以上の整数です。","method":f"整数を計算し、{limit}以下の範囲で調べました。","finding":result,"limits":"この計算だけでは一般的な数学的証明にはなりません。","next_question":"範囲を広げた場合はどうなるでしょう？"},"experiment":{"limit":limit,"algorithm":"trial division","code":"src/prime_lab/engine.py"},"prior_art":"未照合","proof":"なし","provenance":{"llm_used":False,"generator":"Python pilot"}}

def run(day, root=Path(".")):
    folder=root/"data"/"runs"/day
    folder.mkdir(parents=True,exist_ok=True)
    for i in range(1,11):
        path=folder/f"R-{day.replace('-','')}-{i:02d}.json"
        if not path.exists():
            path.write_text(json.dumps(experiment(i,day),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    records=[json.loads(p.read_text(encoding="utf-8")) for p in sorted((root/"data"/"runs").glob("*/*.json"))]
    summary={"updated_at":datetime.now(timezone.utc).isoformat(),"cycles":len(records),"hypotheses":0,"refuted":0,"verified":0,"records":[{"id":r["run_id"],"date":r["date"],"title":r["title"],"status":r["status"],"summary":r["summary"],"plain_language":r["plain_language"]} for r in records]}
    (root/"data"/"research.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return records

if __name__=="__main__":
    import os
    print("Records:",len(run(os.getenv("PRIME_LAB_DATE",datetime.now(timezone.utc).date().isoformat()))))
