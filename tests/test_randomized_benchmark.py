"""Tests that the benchmark helpers stay importable and bounded."""

from src.utils.probability_analysis import bloom_false_positive, miller_rabin_error_bound, summary
from src.utils.random_utils import input_shapes, seeded_list


def test_seeded_list_is_repeatable():
    assert seeded_list(5, 5300) == seeded_list(5, 5300)


def test_shapes_have_the_right_length():
    shapes = input_shapes(20, 5300)
    assert set(shapes) == {"random", "sorted", "reverse", "duplicates"}
    assert all(len(values) == 20 for values in shapes.values())


def test_probability_helpers():
    mu, var = summary([1.0, 2.0, 3.0])
    assert mu == 2.0
    assert var > 0
    assert 0.0 < bloom_false_positive(3, 10, 100) < 1.0
    assert miller_rabin_error_bound(5) < miller_rabin_error_bound(1)
