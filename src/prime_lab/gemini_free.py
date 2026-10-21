"""Single-call Gemini API adapter for PRIME LAB's bounded JSON hypotheses."""
import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from .llm_structured import SYSTEM, parse_candidate

def propose():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY missing; no automatic paid fallback")
    model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if not re.fullmatch(r"gemini-[a-zA-Z0-9.-]+", model):
        raise ValueError("Invalid model")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": "素数の検証可能な剰余仮説をJSONで1件提案してください。"}]}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 800, "responseMimeType": "application/json"}
    }).encode("utf-8")
    req = Request(url, data=payload, headers={"x-goog-api-key": key, "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=90) as response:
            data = json.loads(response.read(100000))
    except HTTPError as error:
        if error.code in (401, 403):
            raise RuntimeError("Gemini API rejected credentials or access (HTTP %s)" % error.code) from None
        if error.code == 404:
            raise RuntimeError("Gemini model unavailable (HTTP 404); check GEMINI_MODEL") from None
        if error.code == 429:
            raise RuntimeError("Gemini free-tier quota exceeded (HTTP 429); no paid fallback") from None
        raise RuntimeError("Gemini API temporarily failed (HTTP %s)" % error.code) from None
    except TimeoutError:
        raise RuntimeError("Gemini response timed out after 90 seconds") from None
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    return parse_candidate(answer)
