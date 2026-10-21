"""Optional LLM idea generator. Never executes model-produced code or claims proof."""
import json
import os
from urllib.request import Request, urlopen

SYSTEM = """あなたはPRIME LABの数学研究課題提案者です。
数学的証明や新発見を主張せず、調査可能な素数の仮説を提案してください。
数論・隣接科学・遠隔分野の着想を区別し、異分野の比喩は数学的定義に翻訳してください。
既知の定理を新発見と呼ばないでください。出典が未確認なら未確認と明記してください。
JSONのみ返してください。必須キー: title, question, conjecture, assumptions, inspiration_field, mathematical_translation, proposed_test, potential_counterexample, beginner_explanation, limitations。
"""
REQUIRED = ("title", "question", "conjecture", "assumptions", "inspiration_field", "mathematical_translation", "proposed_test", "potential_counterexample", "beginner_explanation", "limitations")

def propose(theme, previous=None):
    """Calls a user-configured OpenAI-compatible chat endpoint.

    Configuration: PRIME_LAB_LLM_URL, PRIME_LAB_LLM_MODEL, PRIME_LAB_LLM_KEY.
    The caller must treat the response as an unverified proposal.
    """
    url = os.environ.get("PRIME_LAB_LLM_URL")
    model = os.environ.get("PRIME_LAB_LLM_MODEL")
    key = os.environ.get("PRIME_LAB_LLM_KEY")
    if not all((url, model, key)):
        raise RuntimeError("LLM is not configured; no AI proposal generated")
    if not url.startswith("https://"):
        raise ValueError("LLM endpoint must use HTTPS")
    context = json.dumps((previous or [])[-5:], ensure_ascii=False)[:3000]
    payload = json.dumps({"model": model, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"テーマ: {theme}\n過去の研究要約: {context}\n検証可能な新しい課題案を1件JSONで出力"}
    ], "temperature": 0.6, "max_tokens": 1000}).encode("utf-8")
    request = Request(url, data=payload, headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }, method="POST")
    with urlopen(request, timeout=30) as response:
        body = response.read(100000)
    raw = json.loads(body)["choices"][0]["message"]["content"]
    if raw.strip().startswith("```"):
        raw = raw.strip().split("\n", 1)[1].rsplit("```", 1)[0]
        if raw.startswith("json\n"):
            raw = raw[5:]
    proposal = json.loads(raw)
    if not isinstance(proposal, dict) or any(not isinstance(proposal.get(k), str) or not proposal[k].strip() for k in REQUIRED):
        raise ValueError("LLM proposal did not satisfy required schema")
    return {"status": "未検証のAI提案", "proposal": {k: proposal[k][:4000] for k in REQUIRED}, "model": model, "prior_art": "未照合", "proof": "なし", "executed": False}
