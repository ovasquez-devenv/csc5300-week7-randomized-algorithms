"""MinHash signatures and Jaccard estimates.

Omar Vasquez, CSC 5300 Week 7.
The book mentions MinHash in the Chapter 6 introduction and does not give it
its own section. This file estimates Jaccard with k independent hashes, which
is the same idea as universal hashing in Amakobe section 6.4.2.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, Set


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a = set(left)
    b = set(right)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _hash_token(token: str, index: int, seed: int) -> int:
    return hash((seed, index, token)) & 0xFFFFFFFF


def signature(tokens: Iterable[str], k: int, seed: int = 5300) -> List[int]:
    """MinHash signature of length k."""
    values = list(set(tokens))
    if not values:
        return [0] * k
    sig = []
    for i in range(k):
        sig.append(min(_hash_token(token, i, seed) for token in values))
    return sig


def estimate_jaccard(left: Sequence[str], right: Sequence[str], k: int, seed: int = 5300) -> float:
    left_sig = signature(left, k, seed)
    right_sig = signature(right, k, seed)
    matches = sum(1 for a, b in zip(left_sig, right_sig) if a == b)
    return matches / k


def estimation_error(left: Sequence[str], right: Sequence[str], k: int, seed: int = 5300) -> float:
    return abs(jaccard(left, right) - estimate_jaccard(left, right, k, seed))
