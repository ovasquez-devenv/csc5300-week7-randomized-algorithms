"""Small probability helpers used by the benchmark and the report.

Omar Vasquez, CSC 5300 Week 7.
Amakobe section 6.7 covers expected value and concentration bounds.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return sum((value - mu) ** 2 for value in values) / (len(values) - 1)


def summary(values: Sequence[float]) -> Tuple[float, float]:
    """Sample mean and sample variance."""
    return mean(values), variance(values)


def bloom_false_positive(k: int, n: int, m: int) -> float:
    """Theoretical false positive rate (1 - e^(-kn/m))^k from Amakobe section 6.4.3."""
    if m <= 0 or k <= 0:
        return 1.0
    return (1.0 - math.exp(-k * n / m)) ** k


def miller_rabin_error_bound(k: int) -> float:
    """A common upper bound on the error of k Miller-Rabin rounds is 4^(-k)."""
    return 4.0 ** (-k)
