"""Bloom filter with k hashes and a bit array.

Omar Vasquez, CSC 5300 Week 7.
Amakobe section 6.4.3. Membership is O(k). False positives are possible.
False negatives are not, if the same hashes are used.
"""

from __future__ import annotations

import math
from typing import Iterable, List

from src.utils.random_utils import pair_hash


class BloomFilter:
    def __init__(self, m_bits: int, k_hashes: int, seed: int = 5300) -> None:
        if m_bits < 8 or k_hashes < 1:
            raise ValueError("need a bit array and at least one hash")
        self.m = m_bits
        self.k = k_hashes
        self.seed = seed
        self.bits = bytearray(m_bits)
        self.count = 0

    def _indexes(self, item: str) -> List[int]:
        h1, h2 = pair_hash(item, self.seed)
        return [((h1 + i * h2) % self.m) for i in range(self.k)]

    def add(self, item: str) -> None:
        for index in self._indexes(str(item)):
            self.bits[index] = 1
        self.count += 1

    def check(self, item: str) -> bool:
        return all(self.bits[index] for index in self._indexes(str(item)))

    def load_factor(self) -> float:
        used = sum(self.bits)
        return used / self.m

    def theoretical_fp(self) -> float:
        if self.m == 0:
            return 1.0
        return (1.0 - math.exp(-self.k * self.count / self.m)) ** self.k


def measured_false_positive_rate(
    inserted: Iterable[str],
    queries: Iterable[str],
    m_bits: int,
    k_hashes: int,
    seed: int = 5300,
) -> float:
    """Fraction of absent queries that the filter still reports as present."""
    bloom = BloomFilter(m_bits, k_hashes, seed)
    present = set()
    for item in inserted:
        bloom.add(item)
        present.add(item)
    misses = 0
    checked = 0
    for item in queries:
        if item in present:
            continue
        checked += 1
        if bloom.check(item):
            misses += 1
    if checked == 0:
        return 0.0
    return misses / checked
