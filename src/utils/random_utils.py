"""Seeded helpers for Week 7 randomized algorithms.

Omar Vasquez, CSC 5300 Week 7.
Base seed is 5300, same habit as Week 6.
Hashes use hashlib instead of the built-in hash(). Python salts hash() on
strings with a new random value every time it starts, so the same seed gave
different Bloom filter and MinHash results on each run.
"""

from __future__ import annotations

import hashlib
import random
from typing import Iterable, List, Sequence, Tuple


BASE_SEED = 5300


def make_rng(seed: int = BASE_SEED) -> random.Random:
    """Return a private random generator so tests do not share state."""
    return random.Random(seed)


def seeded_list(n: int, seed: int, low: int = 0, high: int = 10**6) -> List[int]:
    """Build a list of n integers from a seeded generator."""
    rng = make_rng(seed)
    return [rng.randint(low, high) for _ in range(n)]


def input_shapes(n: int, seed: int) -> dict:
    """Random, sorted, reverse, and many-duplicate lists of length n."""
    random_vals = seeded_list(n, seed)
    return {
        "random": random_vals,
        "sorted": sorted(random_vals),
        "reverse": sorted(random_vals, reverse=True),
        "duplicates": [value % 7 for value in random_vals],
    }


def stable_hash(text: str) -> int:
    """32-bit hash that is the same on every run and every machine."""
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big")


def pair_hash(item: str, seed: int) -> Tuple[int, int]:
    """Two independent 32-bit hashes for double hashing. Not cryptographic."""
    text = f"{seed}:{item}"
    h1 = stable_hash(text)
    h2 = stable_hash(text + "#")
    if h2 % 2 == 0:
        h2 += 1
    return h1, h2


def tokens(text: str) -> List[str]:
    """Lowercase word tokens for a small MinHash example."""
    return [part for part in text.lower().split() if part]
