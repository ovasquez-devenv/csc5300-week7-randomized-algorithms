"""Tests for randomized selection."""

from src.randomized.randomized_selection import (
    deterministic_select,
    randomized_select,
    randomized_select_with_depth,
    sort_select,
)


def test_min_median_max():
    data = [9, 1, 5, 3, 7, 2, 8]
    n = len(data)
    for k in (0, n // 2, n - 1):
        assert randomized_select(data, k, seed=5300) == sort_select(data, k)
        assert deterministic_select(data, k) == sort_select(data, k)


def test_depth_is_recorded():
    _, depth = randomized_select_with_depth(list(range(40)), 10, seed=3)
    assert depth >= 1


def test_out_of_range():
    try:
        randomized_select([1, 2], 5)
    except IndexError:
        return
    raise AssertionError("expected IndexError")
