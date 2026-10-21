"""One Gemini call for up to ten structured, independently checked candidates."""
import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from .llm_structured import parse_candidate

def propose_batch(count=10, inspiration=None):
    if count!=10: raise ValueError("Batch size must be 10")
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY missing")
    model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite")
    if not re.fullmatch(r"gemini-[a-zA-Z0-9.-]+",model): raise ValueError("Invalid model")
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    prompt="""あなたは数学の実験計画者。次のJSONオブジェクトのみ返すこと:
{"candidates":[{"kind":"prime_residue","limit":1000,"modulus":6,"residues":[1,5],"motivation":"理由"}]}
candidatesをちょうど10個、異なる検証条件で作る。kindはprime_residue,prime_last_digit,prime_gap_divisibleのいずれか。limitは20から10000、modulusは2から100、residuesは0からmodulus-1の重複なし配列。既知の定理・証明・新発見とは主張しない。初等的な素数の一の位の規則だけに偏らず、素数間隔と剰余を混ぜる。各候補のmotivationは日本語。余計なキーは出さない。"""
    if inspiration:
        prompt += "\\n発想のきっかけとなる単語：" + "、".join(
            str(x["domain"]) + "：" + str(x["word"]) for x in inspiration
        ) + "。比喩のままにせず、必ず検証可能な数学的条件に変換してください。"
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
