"""Quick sort, divide and conquer with a random pivot.
Omar Vasquez, CSC 5300 Week 2.

Copied from my Week 2 submission. The only edits are punctuation in the
docstrings so this file has no em dashes or section signs.

Expected O(n log n). Extra space is mainly the recursion stack (about O(log n)).
Uses a random pivot so sorted or reverse input is not a worst case.
Small leftover pieces (size <= INSERTION_CUTOFF) use insertion sort.
"""
import random
from typing import List, TypeVar

T = TypeVar("T")

# Amakobe section 2.6: insertion sort is cheaper than more partitioning on tiny slices
INSERTION_CUTOFF = 10


def _insertion_sort_range(arr: List[T], low: int, high: int) -> None:
    """Sort arr[low..high] in place with insertion sort (inclusive high)."""
    for i in range(low + 1, high + 1):
        key = arr[i]
        j = i - 1
        while j >= low and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def _partition(arr: List[T], low: int, high: int) -> int:
    """Lomuto partition with a random pivot.

    1. Pick a random index in [low, high] and swap it to high.
    2. Grow a boundary of items <= pivot.
    3. Plant the pivot in its final home and return that index.
    """
    pivot_index = random.randint(low, high)
    arr[pivot_index], arr[high] = arr[high], arr[pivot_index]

    pivot = arr[high]
    boundary = low - 1  # last index known to be <= pivot

    for j in range(low, high):
        if arr[j] <= pivot:
            boundary += 1
            arr[boundary], arr[j] = arr[j], arr[boundary]

    # Pivot sits between the small group and the large group
    plant = boundary + 1
    arr[plant], arr[high] = arr[high], arr[plant]
    return plant


def _quick_sort_range(arr: List[T], low: int, high: int) -> None:
    """In-place quicksort on arr[low..high] (inclusive)."""
    while low < high:
        # Tiny leftover piece: insertion sort, then done with this slice
        if high - low + 1 <= INSERTION_CUTOFF:
            _insertion_sort_range(arr, low, high)
            return

        pivot_pos = _partition(arr, low, high)

        # Recurse on the smaller side first (keeps stack shallower)
        left_size = pivot_pos - low
        right_size = high - pivot_pos
        if left_size < right_size:
            _quick_sort_range(arr, low, pivot_pos - 1)
            low = pivot_pos + 1  # iterate on the larger side
        else:
            _quick_sort_range(arr, pivot_pos + 1, high)
            high = pivot_pos - 1


def quick_sort(arr: List[T]) -> List[T]:
    """Sort a list with randomized quick sort. Returns a new sorted list.

    Divide: choose a random pivot and partition around it.
    Conquer: recursively sort left of pivot and right of pivot.
    Combine: nothing, the pivot is already in its final spot.
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a list")

    if len(arr) <= 1:
        return arr.copy()

    result = arr.copy()
    _quick_sort_range(result, 0, len(result) - 1)
    return result
