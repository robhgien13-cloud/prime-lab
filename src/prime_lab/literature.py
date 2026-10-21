"""Conservative literature triage. Search results are leads, never proof of novelty."""
import json
import re
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

def _get(url, timeout=7):
    req = Request(url, headers={"User-Agent": "PRIME-LAB/0.1 (research literature discovery)"})
    with urlopen(req, timeout=timeout) as response:
        return response.read(150000)

def _terms(record):
    spec = record.get("experiment", {}).get("spec", {})
    kind = spec.get("kind", "")
    return {
        "prime_gap_bound": "consecutive prime gaps",
        "prime_count_window": "primes in short intervals",
        "prime_gap_divisible": "prime gap distribution",
        "prime_residue": "prime residue classes",
        "prime_last_digit": "last digits of primes",
    }.get(kind, "prime number distribution")

def search(record, fetch=_get):
    term = _terms(record)
    urls = {
        "oeis": "https://oeis.org/search?" + urlencode({"q": term, "fmt": "json"}),
        "arxiv": "https://export.arxiv.org/api/query?" + urlencode({"search_query": 'all:"'+term+'"', "start": 0, "max_results": 3}),
        "zbmath": "https://zbmath.org/?q=" + quote(term),
    }
    result = {"query": term, "status": "未確認", "novelty_confirmed": False,
              "sources": {}, "caveat": "検索結果は関連文献の候補に過ぎず、同値性や新規性の判定ではない。"}
    for name in ("oeis", "arxiv"):
        try:
            raw = fetch(urls[name])
            if name == "oeis":
                data = json.loads(raw)
                entries = data.get("results", []) if isinstance(data, dict) else data
                entries = entries if isinstance(entries, list) else []
                hits = [{"id": "A"+str(x.get("number",0)).zfill(6), "title": str(x.get("name",""))[:180]}
                        for x in entries[:3] if isinstance(x, dict) and isinstance(x.get("number"), int)]
            else:
                root = ET.fromstring(raw)
                ns = {"a":"http://www.w3.org/2005/Atom"}
                hits = [{"id": (e.findtext("a:id", default="", namespaces=ns))[:250],
                         "title": " ".join((e.findtext("a:title", default="", namespaces=ns)).split())[:180]}
                        for e in root.findall("a:entry", ns)[:3]]
            result["sources"][name] = {"url": urls[name], "state": "検索済み", "hits": hits}
        except (ValueError, KeyError, OSError, ET.ParseError) as exc:
            result["sources"][name] = {"url": urls[name], "state": "取得失敗", "error_type": type(exc).__name__}
    result["sources"]["zbmath"] = {"url": urls["zbmath"], "state": "検索リンクのみ・自動取得未実装", "hits": []}
    return result

def annotate_recent(root=Path("."), max_records=3, fetch=_get):
    """Only triage a few non-refuted AI records; cache reports beside runs."""
    paths = sorted((root/"data"/"runs").glob("*/*.json"), reverse=True)
    completed = []
    for path in paths:
        if len(completed) >= max_records:
            break
        record = json.loads(path.read_text(encoding="utf-8"))
        if not record.get("provenance",{}).get("llm_used") or "反例発見" in record.get("status",""):
            continue
        output = root/"data"/"literature"/(record["run_id"] + ".json")
        if output.exists():
            continue
        report = {"run_id": record["run_id"], **search(record, fetch=fetch)}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        completed.append(str(output))
    return completed

if __name__ == "__main__":
    print("Literature reports:", annotate_recent())
