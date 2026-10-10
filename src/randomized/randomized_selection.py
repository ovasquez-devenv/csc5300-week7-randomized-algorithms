"""Randomized QuickSelect and a fixed-pivot selection baseline.

Omar Vasquez, CSC 5300 Week 7.
Amakobe section 6.3.3. Expected time is linear. k is the 0-based rank.
"""

from __future__ import annotations

import random
from typing import List, Optional, TypeVar

T = TypeVar("T")


def _partition(arr: List[T], low: int, high: int, rng: Optional[random.Random]) -> int:
    pivot_index = high if rng is None else rng.randint(low, high)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
    pivot = arr[high]
    boundary = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            boundary += 1
            arr[boundary], arr[j] = arr[j], arr[boundary]
    plant = boundary + 1
    arr[plant], arr[high] = arr[high], arr[plant]
    return plant


def _select(
    arr: List[T],
    low: int,
    high: int,
    k: int,
    rng: Optional[random.Random],
    depth: List[int],
) -> T:
    depth[0] += 1
    if low == high:
        return arr[low]
    pivot_pos = _partition(arr, low, high, rng)
    if k == pivot_pos:
        return arr[k]
    if k < pivot_pos:
        return _select(arr, low, pivot_pos - 1, k, rng, depth)
    return _select(arr, pivot_pos + 1, high, k, rng, depth)


def randomized_select(arr: List[T], k: int, seed: int = 5300) -> T:
    """Return the kth smallest item, 0-based, using a random pivot."""
    value, _ = randomized_select_with_depth(arr, k, seed)
    return value


def randomized_select_with_depth(arr: List[T], k: int, seed: int = 5300) -> tuple:
    if not 0 <= k < len(arr):
        raise IndexError("k is out of range")
    work = arr.copy()
    depth = [0]
    value = _select(work, 0, len(work) - 1, k, random.Random(seed), depth)
    return value, depth[0]


def deterministic_select(arr: List[T], k: int) -> T:
    """Fixed last-element pivot. Same partition, no randomness."""
    if not 0 <= k < len(arr):
        raise IndexError("k is out of range")
    work = arr.copy()
    return _select(work, 0, len(work) - 1, k, None, [0])


def sort_select(arr: List[T], k: int) -> T:
    """Deterministic comparison: sort a copy, then index it."""
    return sorted(arr)[k]
