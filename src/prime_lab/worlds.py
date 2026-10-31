"""Experimental integer-world / prime-world correspondences.

These are exploratory models, not definitions asserted by the researcher.
No numerical observation here is a proof of a new prime law.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def primes_through(limit):
    if type(limit) is not int or not 2 <= limit <= 200000:
        raise ValueError("limit must be an integer from 2 to 200000")
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(limit ** .5) + 1):
        if sieve[p]:
            sieve[p * p::p] = b"\x00" * ((limit - p * p) // p + 1)
    return [n for n in range(2, limit + 1) if sieve[n]]

def explore(limit=10000, sample=24):
    """Compare indexed worlds and candidate operations without choosing one."""
    if type(sample) is not int or not 2 <= sample <= 100:
        raise ValueError("sample out of range")
    primes = primes_through(limit)
    if len(primes) < sample + 1:
        raise ValueError("limit too small for sample")
    pairs = [{"integer_index": i + 1, "prime_value": p}
             for i, p in enumerate(primes[:sample])]
    gaps = [primes[i + 1] - primes[i] for i in range(sample)]
    # Candidate transport of addition: a ⊕ b = p_(a+b).
    # Defined only when the resulting index is within the finite sample.
    operations = []
    for a, b in ((1, 1), (1, 2), (2, 3), (3, 4)):
        operations.append({
            "integer_indices": [a, b],
            "integer_sum": a + b,
            "prime_world_sum_candidate": primes[a + b - 1],
            "ordinary_sum_of_prime_values": primes[a - 1] + primes[b - 1],
        })
    # Two prediction baselines, tested out of the training segment.
    split = max(3, sample // 2)
    train_gaps = gaps[:split - 1]
    baseline_gap = round(sum(train_gaps) / len(train_gaps))
    test_indices = list(range(split, sample))
    naive_predictions = [primes[i - 1] + baseline_gap for i in test_indices]
    actual = [primes[i] for i in test_indices]
    errors = [abs(x - y) for x, y in zip(naive_predictions, actual)]
    return {
        "schema_version": "1.0",
        "model_status": "探索用の仮定・未確定",
        "worlds": {
            "integer_world": "1,2,3,... の添字",
            "prime_world": "2,3,5,7,... の素数値",
            "mapping": "n -> p_n（n番目の素数）",
        },
        "sample_pairs": pairs,
        "consecutive_prime_gaps": gaps,
        "candidate_transport_operations": operations,
        "prediction_baseline": {
            "method": "前半の平均素数間隔を後半に適用する単純な比較基準",
            "train_indices": [1, split],
            "test_indices": [split + 1, sample],
            "rounded_gap": baseline_gap,
            "absolute_errors": errors,
            "mean_absolute_error": sum(errors) / len(errors),
            "exact_matches": sum(x == y for x, y in zip(naive_predictions, actual)),
        },
        "open_questions": [
            "対応を通じた演算は研究上有用か、それとも単なる記号の置換か",
            "素数間隔に予測可能な構造があるか",
            "各素数を起点とする局所世界をどう定義するか",
            "より大きな範囲で仮説が維持されるか",
        ],
        "caution": "演算は候補であり採用済みの定義ではない。有限計算は証明でなく、予測基準も新発見ではない。",
    }

def run(root=Path("."), day=None, limit=10000, sample=24):
    day = day or datetime.now(timezone.utc).date().isoformat()
    if datetime.strptime(day, "%Y-%m-%d").strftime("%Y-%m-%d") != day:
        raise ValueError("invalid date")
    output = root / "data" / "worlds" / (day + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    data = {"date": day, **explore(limit, sample)}
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output

if __name__ == "__main__":
    limit = int(os.environ.get("WORLD_LIMIT", "10000"))
    sample = int(os.environ.get("WORLD_SAMPLE", "24"))
    print(run(limit=limit, sample=sample))
