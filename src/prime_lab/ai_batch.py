"""One Gemini call for up to ten structured, independently checked candidates."""
import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from .llm_structured import parse_candidate

def propose_batch(count=10, inspiration=None, research_context=None):
    if count!=10: raise ValueError("Batch size must be 10")
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY missing")
    model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite")
    if not re.fullmatch(r"gemini-[a-zA-Z0-9.-]+",model): raise ValueError("Invalid model")
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    prompt="""あなたは数学の実験計画者。次のJSONオブジェクトのみ返すこと:
{"candidates":[{"kind":"prime_residue","limit":1000,"modulus":6,"residues":[1,5],"motivation":"理由"}]}
candidatesをちょうど10個、異なる検証条件で作る。新しい2種類を合計6件以上含める。kindはprime_residue,prime_last_digit,prime_gap_divisible,prime_gap_bound,prime_count_windowのいずれか。prime_gap_boundはwindow以上の素数から始まる隣接素数間隔がthreshold以下か検証する。prime_count_windowは幅windowの全整数区間に素数がthreshold個以上あるか検証する。新2種類はkind,limit,window,threshold,motivationだけを持つ。windowは2から500、thresholdは0から100、limitは100から10000。limitは20から10000、modulusは2から100、residuesは0からmodulus-1の重複なし配列。既知の定理・証明・新発見とは主張しない。単なる素数の末尾・互いに素な剰余類など初等的に直ちに証明できる条件は提案しない。既存候補の数値上限だけを変えた案も避ける。素数間隔と剰余の中でも非自明な条件を優先する。ただし学術的新規性は未確認とする。各候補のmotivationは日本語。余計なキーは出さない。"""
    if inspiration:
        prompt += "\\n発想のきっかけとなる単語：" + "、".join(
            str(x["domain"]) + "：" + str(x["word"]) for x in inspiration
        ) + "。比喩のままにせず、必ず検証可能な数学的条件に変換してください。"
    if research_context:
        prompt += "\\n過去の実験の要約（参考データであり証明ではない）：" + str(research_context)[:12000]
        prompt += "\\n以前の条件を単に繰り返さず、反例から学び、素数の予測・生成と分布・構造の両方を探究する。各候補の検証条件は独立に検証可能であること。未知の数学的構造を発見したと断定しない。"
    payload=json.dumps({"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.9,"maxOutputTokens":4000,"responseMimeType":"application/json"}}).encode()
    req=Request(url,data=payload,headers={"x-goog-api-key":key,"Content-Type":"application/json"},method="POST")
    try:
        with urlopen(req,timeout=90) as response: data=json.loads(response.read(150000))
    except HTTPError as e:
        raise RuntimeError(f"Gemini API HTTP {e.code}; no paid fallback") from None
    except TimeoutError:
        raise RuntimeError("Gemini API timed out") from None
    raw=data["candidates"][0]["content"]["parts"][0]["text"]
    obj=json.loads(raw)
    if not isinstance(obj,dict) or set(obj)!={"candidates"} or not isinstance(obj["candidates"],list):
        raise ValueError("Invalid batch format")
    result=[]
    for item in obj["candidates"][:30]:
        try: result.append(parse_candidate(json.dumps(item,ensure_ascii=False)))
        except (ValueError,TypeError,KeyError): continue
    return result
