"""Single-call Gemini API adapter for PRIME LAB's bounded JSON hypotheses."""
import json
import os
import re
from urllib.request import Request, urlopen
from .llm_structured import SYSTEM, parse_candidate

def propose():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY missing; no automatic paid fallback")
    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
    if not re.fullmatch(r"gemini-[a-zA-Z0-9.-]+", model):
        raise ValueError("Invalid model")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": "素数の検証可能な剰余仮説をJSONで1件提案してください。"}]}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 800, "responseMimeType": "application/json"}
    }).encode("utf-8")
    req = Request(url, data=payload, headers={"x-goog-api-key": key, "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=30) as response:
        data = json.loads(response.read(100000))
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    return parse_candidate(answer)
