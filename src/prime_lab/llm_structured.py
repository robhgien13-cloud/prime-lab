"""Generate a constrained prime hypothesis with an optional configured LLM.

The returned JSON is checked for type/range safety, but its *mathematical*
meaning, novelty and consistency with the model's explanation are unverified.
No model-produced code is executed.
"""
import json
import os
from urllib.request import Request, urlopen
from .structured import validate, verify

SYSTEM = """あなたは素数の数学研究における仮説提案者です。
自由なコードを生成しないでください。必ずJSONオブジェクトのみ返してください。
JSONには "kind", "limit", "modulus", "residues", "motivation" の5つだけ含めてください。
kindはprime_residue, prime_last_digit, prime_gap_divisible, prime_gap_bound, prime_count_window, twin_prime_count_window, prime_count_window_at_most, prime_gap_lower_boundのいずれか。
limitは20以上10000以下の整数、modulusは2以上100以下の整数、
residuesは0以上modulus未満の重複のない整数配列です。
motivationはなぜその余りの規則を調べる価値があると思うか、やさしい日本語で説明。
実験結果、証明、新発見、先行研究調査済みなどと主張しないでください。"""

def parse_candidate(raw):
    if not isinstance(raw, str) or len(raw) > 20000:
        raise ValueError("Invalid response size")
    data = json.loads(raw)
    if not isinstance(data, dict) or set(data) not in ({"kind","limit","modulus","residues","motivation"}, {"kind","limit","window","threshold","motivation"}):
        raise ValueError("Invalid candidate fields")
    if not isinstance(data["motivation"], str) or not 1 <= len(data["motivation"]) <= 1000:
        raise ValueError("Invalid motivation")
    spec = {k:v for k,v in data.items() if k != "motivation"}
    validate(spec)
    return {"spec":spec,"motivation":data["motivation"],"origin":"LLM proposal (unverified)"}

def propose():
    url=os.getenv("PRIME_LAB_LLM_URL")
    model=os.getenv("PRIME_LAB_LLM_MODEL")
    key=os.getenv("PRIME_LAB_LLM_KEY")
    if not all((url,model,key)):
        raise RuntimeError("LLM is not configured")
    if not url.startswith("https://"):
        raise ValueError("HTTPS endpoint required")
    payload=json.dumps({"model":model,"messages":[{"role":"system","content":SYSTEM},
        {"role":"user","content":"素数に関する、検証可能で興味深い剰余の仮説を1つJSONで提案してください。"}],
        "temperature":0.7,"max_tokens":600}).encode("utf-8")
    req=Request(url,data=payload,headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=30) as resp:
        body=resp.read(100000)
    answer=json.loads(body)["choices"][0]["message"]["content"]
    return parse_candidate(answer)

def experiment_candidate(candidate):
    if not isinstance(candidate,dict) or set(candidate) != {"spec","motivation","origin"}:
        raise ValueError("Invalid candidate")
    if candidate["origin"] != "LLM proposal (unverified)":
        raise ValueError("Unexpected origin")
    outcome=verify(candidate["spec"])
    return {
        "candidate":candidate,
        "finite_check":outcome,
        "model_text_matches_spec":"未確認",
        "novelty":"未確認",
        "proof":"なし",
        "ai_hypothesis_verified":False,
        "plain_language":{
            "question":outcome["statement"]+"という条件を調べました。",
            "background":"素数は1と自分自身以外では割り切れない2以上の整数です。",
            "method":f"{outcome['limit']}以下の対象を計算しました。",
            "finding":outcome["beginner_explanation"],
            "limits":"AIの説明と検証条件が一致するかは未確認です。計算は証明ではありません。",
            "next_question":"この予想は既知の定理でしょうか。理由を説明できるでしょうか。",
        }
    }
