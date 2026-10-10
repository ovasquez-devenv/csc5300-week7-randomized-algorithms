"""Randomized QuickSort and a fixed-pivot baseline.

Omar Vasquez, CSC 5300 Week 7.
Amakobe section 6.2.2 uses a random pivot so the expected cost is O(n log n).
The Week 2 file already used a random pivot, so the deterministic function
in this file is a new fixed last-element pivot on the same Lomuto partition.
"""

from __future__ import annotations

import random
from typing import List, Optional, TypeVar

T = TypeVar("T")
INSERTION_CUTOFF = 10


def _insertion_sort_range(arr: List[T], low: int, high: int, comparisons: List[int]) -> None:
    for i in range(low + 1, high + 1):
        key = arr[i]
        j = i - 1
        while j >= low:
            comparisons[0] += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = key


def _partition(
    arr: List[T],
    low: int,
    high: int,
    rng: Optional[random.Random],
    comparisons: List[int],
) -> int:
    if rng is None:
        pivot_index = high
    else:
        pivot_index = rng.randint(low, high)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]
    pivot = arr[high]
    boundary = low - 1
    for j in range(low, high):
        comparisons[0] += 1
        if arr[j] <= pivot:
            boundary += 1
            arr[boundary], arr[j] = arr[j], arr[boundary]
    plant = boundary + 1
    arr[plant], arr[high] = arr[high], arr[plant]
    return plant


def _sort_range(
    arr: List[T],
    low: int,
    high: int,
    rng: Optional[random.Random],
    comparisons: List[int],
) -> None:
    while low < high:
        if high - low + 1 <= INSERTION_CUTOFF:
            _insertion_sort_range(arr, low, high, comparisons)
            return
        pivot_pos = _partition(arr, low, high, rng, comparisons)
        left_size = pivot_pos - low
        right_size = high - pivot_pos
        if left_size < right_size:
            _sort_range(arr, low, pivot_pos - 1, rng, comparisons)
            low = pivot_pos + 1
        else:
            _sort_range(arr, pivot_pos + 1, high, rng, comparisons)
            high = pivot_pos - 1


def randomized_quicksort(arr: List[T], seed: int = 5300) -> List[T]:
    """Return a new sorted list. Pivot is random at each step."""
    result, _ = randomized_quicksort_with_comparisons(arr, seed)
    return result


def randomized_quicksort_with_comparisons(arr: List[T], seed: int = 5300) -> tuple:
    """Sort and return (sorted copy, comparison count)."""
    rng = random.Random(seed)
    result = arr.copy()
    comparisons = [0]
    if len(result) > 1:
        _sort_range(result, 0, len(result) - 1, rng, comparisons)
    return result, comparisons[0]


def deterministic_quicksort(arr: List[T]) -> List[T]:
    """Same Lomuto partition and cutoff, but the pivot is always the last element.

    This is the deterministic baseline. It is not the Week 2 submission.
    Sorted or reverse input is the bad case.
    """
    result, _ = deterministic_quicksort_with_comparisons(arr)
    return result


def deterministic_quicksort_with_comparisons(arr: List[T]) -> tuple:
    result = arr.copy()
    comparisons = [0]
    if len(result) > 1:
        _sort_range(result, 0, len(result) - 1, None, comparisons)
    return result, comparisons[0]
