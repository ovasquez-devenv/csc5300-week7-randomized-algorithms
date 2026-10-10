"""Fermat and Miller-Rabin primality tests, plus trial division.

Omar Vasquez, CSC 5300 Week 7.
Amakobe section 6.2.3. These Monte Carlo tests are always fast and usually right.
"""

from __future__ import annotations

import random
from typing import Iterable, List


def trial_division_is_prime(n: int) -> bool:
    """Deterministic check. Fine for moderate n, slow past about 10**7."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def fermat_is_prime(n: int, k: int = 5, seed: int = 5300) -> bool:
    """Fermat test. Carmichael numbers can pass even when they are composite."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    rng = random.Random(seed)
    for _ in range(k):
        a = rng.randrange(2, n - 1)
        if pow(a, n - 1, n) != 1:
            return False
    return True


def miller_rabin_is_prime(n: int, k: int = 5, seed: int = 5300) -> bool:
    """Miller-Rabin. A composite that passes all k rounds is a strong liar case."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    rng = random.Random(seed)
    for _ in range(k):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        witness = False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                witness = True
                break
        if not witness:
            return False
    return True


CARMICHAEL = (561, 1105, 1729, 2465, 2821, 6601)
