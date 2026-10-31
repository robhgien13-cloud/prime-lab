"""Finite logarithmic comparisons for prime distributions; not a proof."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

def analyze(limit=10000):
    if type(limit) is not int or not 100 <= limit <= 200000:
        raise ValueError("limit must be 100..200000")
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p*p::p] = b"\x00" * ((limit-p*p)//p+1)
    primes = [i for i in range(2,limit+1) if sieve[i]]
    checkpoints = sorted(set([100,1000,10000,100000,limit]))
    counts = []
    for x in checkpoints:
        if x > limit: continue
        n = sum(p <= x for p in primes)
        estimate = x / math.log(x)
        counts.append({"x":x,"actual":n,"x_over_ln_x":estimate,"error":n-estimate,"relative_error":(n-estimate)/n})
    gaps = [b-a for a,b in zip(primes,primes[1:])]
    normalized = [g/math.log(p) for p,g in zip(primes,gaps)]
    indices = sorted(set([10,100,1000,len(primes)]))
    indexed = [{"n":n,"prime":primes[n-1],"n_ln_n":n*math.log(n),"ratio":primes[n-1]/(n*math.log(n))} for n in indices if n <= len(primes)]
    return {"schema_version":"1.0","limit":limit,"prime_count":len(primes),
            "prime_count_comparison":counts,"indexed_prime_comparison":indexed,
            "gap_over_ln_prime":{"count":len(normalized),"mean":sum(normalized)/len(normalized),"min":min(normalized),"max":max(normalized)},
            "caution":"x/ln(x)とn ln(n)は漸近比較用。個々の素数間隔の予測や数学的証明ではない。"}
def run(root=Path("."), day=None, limit=10000):
    day = day or datetime.now(timezone.utc).date().isoformat()
    datetime.strptime(day,"%Y-%m-%d")
    path = root/"data"/"log_analysis"/(day+".json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({"date":day,**analyze(limit)},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return path
if __name__ == "__main__":
    import os
    print(run(limit=int(os.getenv("WORLD_LIMIT","10000"))))
