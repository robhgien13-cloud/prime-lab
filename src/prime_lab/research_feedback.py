"""Summarize prior experiments for the next day's prime research.
No mathematical discovery is inferred from finite checks.
"""
import json
from collections import Counter
from pathlib import Path

THEMES = (
    "prime_gap_bound", "prime_count_window", "prime_gap_divisible",
    "prime_residue", "prime_last_digit", "twin_prime_count_window", "prime_count_window_at_most", "prime_gap_lower_bound", "cousin_prime_count_window", "sexy_prime_count_window", "prime_triplet_count_window", "small_gap_count_window",
)
RESEARCH_GOALS = (
    "素数の予測・生成に関する検証可能な規則の探索",
    "素数の分布・構造・間隔に関する規則の探索",
    "小さな整数世界を拡張する着想の検討（数学的定義が必要）",
    "双子素数と素数間隔の構造の探索",
)

def summarize(root=Path("."), max_records=200):
    """Read existing structured experiments; return a bounded, safe summary."""
    if not 1 <= max_records <= 1000:
        raise ValueError("Invalid max_records")
    paths = sorted((root / "data" / "runs").glob("*/*.json"), reverse=True)
    counts = Counter()
    examples = []
    seen = set()
    for path in paths:
        if sum(counts.values()) >= max_records:
            break
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        spec = record.get("experiment", {}).get("spec")
        if not isinstance(spec, dict) or spec.get("kind") not in THEMES:
            continue
        # Deduplicate by mathematical conditions, not only file name.
        fingerprint = json.dumps({k: v for k, v in spec.items() if k != "limit"},
                                 sort_keys=True, ensure_ascii=False)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        status = str(record.get("status", "不明"))
        counts[spec["kind"]] += 1
        if len(examples) < 12:
            examples.append({
                "kind": spec["kind"],
                "parameters": {k: v for k, v in spec.items() if k != "limit"},
                "outcome": status[:100],
            })
    world_results = []
    for path in sorted((root / "data" / "worlds").glob("*.json"), reverse=True)[:5]:
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
            baseline = item.get("prediction_baseline", {})
            world_results.append({
                "date": item.get("date"),
                "mapping": item.get("worlds", {}).get("mapping"),
                "sample_size": len(item.get("sample_pairs", [])),
                "baseline_exact_matches": baseline.get("exact_matches"),
                "baseline_mae": baseline.get("mean_absolute_error"),
                "caution": "有限実験であり、新規性・証明は未確認",
            })
        except (ValueError, OSError, AttributeError, TypeError):
            continue
    return {
        "prime_world_experiments": world_results,
        "goals": list(RESEARCH_GOALS),
        "distinct_conditions_reviewed": sum(counts.values()),
        "by_kind": dict(counts),
        "recent_examples": examples,
        "limits": "有限計算は証明でない。新規性は文献との厳密な照合が必要。",
    }

def literature_context(root=Path("."), max_reports=8):
    """Use stored literature search leads, never infer novelty from search hits."""
    reports = []
    for path in sorted((root / "data" / "literature").glob("*.json"), reverse=True):
        if len(reports) >= max_reports:
            break
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        sources = item.get("sources", {})
        hits = []
        for provider in ("arxiv", "oeis"):
            for hit in sources.get(provider, {}).get("hits", [])[:3]:
                if isinstance(hit, dict):
                    hits.append({"provider": provider, "id": str(hit.get("id", ""))[:250],
                                 "title": str(hit.get("title", ""))[:180]})
        reports.append({"run_id": item.get("run_id"), "query": item.get("query"),
                        "hits": hits, "novelty_confirmed": False})
    return {"literature_search_leads": reports,
            "established_background": [
                {"topic": "素数定理", "fact": "大きなxに対してπ(x)はx/log(x)に漸近する",
                 "reference": "https://encyclopediaofmath.org/wiki/Prime_number_theorem"},
                {"topic": "ディリクレの算術級数定理", "fact": "aとqが互いに素ならa mod qに属する素数は無限にある",
                 "reference": "https://encyclopediaofmath.org/wiki/Dirichlet_theorem"},
                {"topic": "有界素数間隔", "fact": "隣接素数間隔がある固定定数以下となる例が無限に存在することは既知",
                 "reference": "https://arxiv.org/abs/1305.6284"}
            ],
            "warning": "参考知識と検索候補。論文本文の精読・同値性・新規性判定は未実施。"}


# Curated background references; matching by experiment family is not proof of use.
BACKGROUND_BY_KIND = {
    "prime_residue": ("ディリクレの算術級数定理", "https://encyclopediaofmath.org/wiki/Dirichlet_theorem", "素数の合同類"),
    "prime_last_digit": ("ディリクレの算術級数定理", "https://encyclopediaofmath.org/wiki/Dirichlet_theorem", "素数の合同類"),
    "prime_gap_divisible": ("素数間隔の研究", "https://arxiv.org/abs/1305.6284", "素数間隔"),
    "prime_gap_bound": ("有界素数間隔", "https://arxiv.org/abs/1305.6284", "素数間隔"),
    "prime_gap_lower_bound": ("有界素数間隔", "https://arxiv.org/abs/1305.6284", "素数間隔"),
    "prime_count_window": ("素数定理", "https://encyclopediaofmath.org/wiki/Prime_number_theorem", "素数の分布"),
    "prime_count_window_at_most": ("素数定理", "https://encyclopediaofmath.org/wiki/Prime_number_theorem", "素数の分布"),
    "twin_prime_count_window": ("有界素数間隔", "https://arxiv.org/abs/1305.6284", "素数間隔"),
    "cousin_prime_count_window": ("有界素数間隔", "https://arxiv.org/abs/1305.6284", "素数間隔"),
    "sexy_prime_count_window": ("有界素数間隔", "https://arxiv.org/abs/1305.6284", "素数間隔"),
    "prime_triplet_count_window": ("有界素数間隔", "https://arxiv.org/abs/1305.6284", "素数間隔"),
    "small_gap_count_window": ("有界素数間隔", "https://arxiv.org/abs/1305.6284", "素数間隔"),
}

def reference_for_experiment(spec, motivation=""):
    """Attach an auditable topic-matched reference, not an invented LLM citation."""
    kind = spec.get("kind") if isinstance(spec, dict) else None
    item = BACKGROUND_BY_KIND.get(kind)
    if item is None:
        return {"sources": [], "selection_basis": "対応する参考文献なし",
                "citation_status": "未照合"}
    title, url, topic = item
    return {"sources": [{"title": title, "url": url, "topic": topic,
                         "relationship": "実験テーマに関連する既存研究の参考資料（自動割当）"}],
            "selection_basis": "検証の種類「" + str(kind) + "」に基づき参考資料を自動選択。"
                 + "仮説提案の動機（未検証）：" + str(motivation)[:350],
            "citation_status": "関連資料の候補・本文との対応および新規性は未確認",
            "model_used_source": "不明"}

def prompt_context(root=Path(".")):
    return json.dumps({"prior_experiments": summarize(root), "prior_research": literature_context(root)}, ensure_ascii=False, separators=(",", ":"))
