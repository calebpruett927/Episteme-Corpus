# src/umcp/eid.py
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, List, Sequence


def _sieve_primes_upto(n: int) -> List[int]:
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    p = 2
    while p * p <= n:
        if sieve[p]:
            step = p
            start = p * p
            sieve[start:n + 1:step] = b"\x00" * (((n - start) // step) + 1)
        p += 1
    return [i for i in range(2, n + 1) if sieve[i]]


def prime_pi(n: int) -> int:
    """π(n): number of primes ≤ n."""
    return len(_sieve_primes_upto(int(n)))


def _first_k_primes(k: int) -> List[int]:
    if k <= 0:
        return []
    # Simple increasing sieve bound; sufficient for checksums and small/medium k.
    # Upper bound for nth prime: n(log n + log log n) for n>=6
    if k < 6:
        bound = 15
    else:
        bound = int(k * (math.log(k) + math.log(math.log(k)))) + 10
    primes: List[int] = []
    while len(primes) < k:
        primes = _sieve_primes_upto(bound)
        bound *= 2
    return primes[:k]


@dataclass(frozen=True, slots=True)
class EIDCounts:
    """
    EID counts container for prime-calibrated checksum + “mass”.

    Intended usage: store nonnegative integer counts.
    """
    counts: Sequence[int]

    @property
    def n(self) -> int:
        return len(self.counts)

    @property
    def mass(self) -> int:
        return int(sum(int(x) for x in self.counts))

    @property
    def pi_n(self) -> int:
        return prime_pi(self.n)

    def checksum(self) -> int:
        return eid_checksum(self.counts)


def eid_checksum(counts: Sequence[int]) -> int:
    """
    Prime-weighted checksum over counts.

    checksum = sum_i counts[i] * p_{i+1}  (mod 2^64)
    """
    k = len(counts)
    primes = _first_k_primes(k)
    acc = 0
    mod = 2**64
    for i, c in enumerate(counts):
        acc = (acc + (int(c) * primes[i])) % mod
    return acc


def delta_kappa_eid(pre: EIDCounts | Sequence[int], post: EIDCounts | Sequence[int], eps: float = 1e-12) -> float:
    """
    Prime-calibrated delta κ based on EID “mass” ratio:

      Δκ = ln( (mass_post + eps) / (mass_pre + eps) )

    This is intentionally minimal and audit-friendly.
    """
    pre_counts = pre.counts if isinstance(pre, EIDCounts) else pre
    post_counts = post.counts if isinstance(post, EIDCounts) else post

    m0 = float(sum(int(x) for x in pre_counts))
    m1 = float(sum(int(x) for x in post_counts))
    return math.log((m1 + eps) / (m0 + eps))
