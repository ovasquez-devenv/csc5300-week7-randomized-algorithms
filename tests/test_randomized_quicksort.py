"""Tests for randomized and deterministic quicksort."""

from src.randomized.randomized_quicksort import (
    deterministic_quicksort,
    randomized_quicksort,
    randomized_quicksort_with_comparisons,
)
from src.randomized.week2_quicksort import quick_sort


def test_randomized_matches_sorted():
    data = [5, 1, 4, 2, 9, 1, 3]
    assert randomized_quicksort(data, seed=5300) == sorted(data)


def test_deterministic_matches_sorted_on_random_input():
    data = [8, 3, 1, 7, 2, 6]
    assert deterministic_quicksort(data) == sorted(data)


def test_week2_copy_still_sorts():
    data = [4, 4, 1, 9, 0]
    assert quick_sort(data) == sorted(data)


def test_comparisons_are_positive_for_long_input():
    data = list(range(50, 0, -1))
    _, count = randomized_quicksort_with_comparisons(data, seed=7)
    assert count > 0


def test_does_not_mutate_input():
    data = [3, 1, 2]
    randomized_quicksort(data, seed=1)
    assert data == [3, 1, 2]
