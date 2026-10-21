"""Deterministic exploratory scans: observations, not mathematical discoveries."""
from math import log
from .engine import prime

def scan(limit=10000):
    if type(limit) is not int or not 100 <= limit <= 10000:
        raise ValueError("limit must be between 100 and 10000")
    ps = [n for n in range(2, limit + 1) if prime(n)]
    windows = []
    for start in (100, 1000, 5000):
        end = min(start * 2, limit)
        if end <= start:
            continue
        group = [p for p in ps if start <= p < end]
        gaps = [b-a for a,b in zip(group, group[1:])]
        width = end-start
        expected = width / log((start+end)/2)
        windows.append({
            "start": start, "end_exclusive": end,
            "prime_count": len(group),
            "reference_count": round(expected, 3),
            "count_to_reference_ratio": round(len(group)/expected, 4),
            "mean_internal_gap": round(sum(gaps)/len(gaps), 4) if gaps else None,
            "max_internal_gap": max(gaps) if gaps else None,
        })
    ranked = sorted(windows, key=lambda w: abs(w["count_to_reference_ratio"]-1), reverse=True)
    observations = [{
        "kind": "prime_count_deviation",
        "window": [w["start"], w["end_exclusive"]],
        "observed": w["prime_count"],
        "reference": w["reference_count"],
        "ratio": w["count_to_reference_ratio"],
        "note": "素数定理に基づく粗い参考値との比較。有限区間の差は新発見を意味しない。",
    } for w in ranked]
    return {
        "schema_version": "1.0", "limit": limit,
        "method": "exact prime enumeration and rough prime-number-theorem reference",
        "windows": windows, "observations": observations,
        "research_question": "区間の位置と幅を変えたとき、素数個数の参考値からのずれはどう変化するか",
        "novelty": "未確認", "proof": "なし",
        "limits": "探索的記述統計。先行研究の照合・統計的有意性評価・数学的証明は行っていない。",
    }
