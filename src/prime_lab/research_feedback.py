"""Summarize prior experiments for the next day's prime research.
No mathematical discovery is inferred from finite checks.
"""
import json
from collections import Counter
from pathlib import Path

THEMES = (
    "prime_gap_bound", "prime_count_window", "prime_gap_divisible",
    "prime_residue", "prime_last_digit",
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

def prompt_context(root=Path(".")):
    return json.dumps(summarize(root), ensure_ascii=False, separators=(",", ":"))
