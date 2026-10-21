"""Safe finite verifier for user/AI-proposed *structured* prime conjectures.

The input is declarative JSON, not executable Python. This verifier makes
no claims about mathematical proof, originality, or prior literature.
"""
from __future__ import annotations
from .engine import prime

MAX_LIMIT = 10000
ALLOWED = {"prime_residue", "prime_gap_divisible", "prime_last_digit", "prime_gap_bound", "prime_count_window"}

def validate(spec):
    if not isinstance(spec, dict):
        raise ValueError("Expected dict")
    if spec.get("kind") in {"prime_gap_bound", "prime_count_window"}:
        if set(spec) != {"kind", "limit", "window", "threshold"}:
            raise ValueError("Invalid expanded spec")
        limit, window, threshold = spec["limit"], spec["window"], spec["threshold"]
        if type(limit) is not int or not 100 <= limit <= MAX_LIMIT or type(window) is not int or not 2 <= window <= 500 or type(threshold) is not int or not 0 <= threshold <= 100:
            raise ValueError("Invalid range")
        return spec["kind"], limit, window, threshold
    if set(spec) != {"kind", "limit", "modulus", "residues"}:
        raise ValueError("Expected kind, limit, modulus, residues")
    kind, limit, modulus, residues = (spec[k] for k in ("kind", "limit", "modulus", "residues"))
    if not isinstance(kind, str) or kind not in ALLOWED or type(limit) is not int or not 20 <= limit <= MAX_LIMIT:
        raise ValueError("Invalid kind or limit")
    if type(modulus) is not int or not 2 <= modulus <= 100:
        raise ValueError("Invalid modulus")
    if not isinstance(residues, list) or not 1 <= len(residues) <= modulus:
        raise ValueError("Invalid residues")
    if any(type(r) is not int or not 0 <= r < modulus for r in residues) or len(set(residues)) != len(residues):
        raise ValueError("Residues must be distinct integers modulo modulus")
    return kind, limit, modulus, set(residues)

def verify(spec):
    kind, limit, modulus, residues = validate(spec)
    ps = [n for n in range(2, limit + 1) if prime(n)]
    if kind in {"prime_gap_bound", "prime_count_window"}:
        window, threshold = modulus, residues
        if kind == "prime_gap_bound":
            items = [(a, b-a) for a,b in zip(ps, ps[1:]) if a >= window]
            statement = f"{window}以上の素数から始まる隣接素数間隔は常に{threshold}以下"
            bad = next(((n,v) for n,v in items if v > threshold), None)
        else:
            items = []
            left = right = 0
            for start in range(2, limit-window+2):
                while left < len(ps) and ps[left] < start:
                    left += 1
                if right < left: right = left
                while right < len(ps) and ps[right] < start+window:
                    right += 1
                items.append((start, right-left))
            statement = f"幅{window}のすべての整数区間には素数が{threshold}個以上存在する"
            bad = next(((n,v) for n,v in items if v < threshold), None)
        return {
            "spec":spec,"statement":statement,
            "status":"有限範囲で反例発見" if bad else "有限範囲で反例なし",
            "counterexample":{"number":bad[0],"observed_value":bad[1]} if bad else None,
            "tested_cases":len(items) if bad is None else next(i for i,x in enumerate(items,1) if x==bad),
            "limit":limit,"mathematically_proven":False,"novelty":"未確認",
            "beginner_explanation":f"{bad[0]}で観測値{bad[1]}が条件に反しました。" if bad else f"{limit}以下では反例が見つかりませんでした。証明ではありません。"
        }
    if kind == "prime_residue":
        # Check all primes greater than modulus, to avoid small prime divisors.
        items = [(p, p % modulus) for p in ps if p > modulus]
        statement = f"{modulus}より大きいすべての素数pについて、pを{modulus}で割った余りが{sorted(residues)}に含まれる"
    elif kind == "prime_last_digit":
        items = [(p, p % modulus) for p in ps if p > modulus]
        statement = f"{modulus}より大きいすべての素数pの余りが{sorted(residues)}に含まれる"
    else:
        items = [(b, (b-a) % modulus) for a, b in zip(ps, ps[1:])]
        statement = f"隣り合う素数の差を{modulus}で割った余りが{sorted(residues)}に含まれる"
    bad = next(((n, r) for n, r in items if r not in residues), None)
    return {
        "spec": spec,
        "statement": statement,
        "status": "有限範囲で反例発見" if bad else "有限範囲で反例なし",
        "counterexample": {"number": bad[0], "observed_remainder": bad[1]} if bad else None,
        "tested_cases": len(items) if bad is None else next(i for i, x in enumerate(items, 1) if x == bad),
        "limit": limit,
        "mathematically_proven": False,
        "novelty": "未確認",
        "beginner_explanation": (
            f"{bad[0]}で予想と異なる余り{bad[1]}が出ました。" if bad
            else f"{limit}以下の対象を調べましたが反例はありませんでした。無限に続くことは証明していません。"
        ),
    }
