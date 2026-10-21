"""Safe, bounded mathematical checks for structured hypotheses.

No eval, exec, arbitrary code, or natural-language claim interpretation.
Passing a finite check is NOT a proof of a universal statement.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .engine import prime

ALLOWED = {"prime_mod_6", "twin_prime_gap", "goldbach_even"}
MAX_LIMIT = 10000

def validate_spec(spec: dict[str, Any]) -> tuple[str, int]:
    if not isinstance(spec, dict):
        raise ValueError("spec must be a JSON object")
    if set(spec) != {"kind", "limit"}:
        raise ValueError("only kind and limit are permitted")
    kind, limit = spec["kind"], spec["limit"]
    if not isinstance(kind, str) or kind not in ALLOWED:
        raise ValueError("unknown hypothesis kind")
    if type(limit) is not int or not 20 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be an integer from 20 to 10000")
    return kind, limit

def check(spec: dict[str, Any]) -> dict[str, Any]:
    kind, limit = validate_spec(spec)
    cases = 0
    counterexample = None
    if kind == "prime_mod_6":
        statement = "3より大きいすべての素数は、6で割ると1か5余る"
        candidates = [n for n in range(4, limit + 1) if prime(n)]
        condition = lambda n: n % 6 in (1, 5)
    elif kind == "twin_prime_gap":
        statement = "差が2の素数の組は、3と5を除き6の倍数を挟む"
        candidates = [n for n in range(3, limit - 1) if prime(n) and prime(n + 2) and n != 3]
        condition = lambda n: (n + 1) % 6 == 0
    else:
        statement = "4以上の偶数は、2つの素数の和で表せる"
        candidates = list(range(4, limit + 1, 2))
        condition = lambda n: any(prime(p) and prime(n - p) for p in range(2, n // 2 + 1))
    for n in candidates:
        cases += 1
        if not condition(n):
            counterexample = n
            break
    return {
        "kind": kind, "statement": statement, "limit": limit,
        "tested_cases": cases, "counterexample": counterexample,
        "status": "反証済み（範囲内の反例）" if counterexample is not None else "有限範囲で反例なし（未証明）",
        "proof": False, "novelty": "未確認",
        "explanation": (f"{cases}件を検査し、反例{counterexample}が見つかりました。" if counterexample is not None
                        else f"{cases}件を検査し反例はありませんでした。ただし、範囲外の数については証明していません。"),
    }
