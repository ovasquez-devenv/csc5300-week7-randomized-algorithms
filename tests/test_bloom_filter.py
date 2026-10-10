"""Tests for the Bloom filter."""

from src.randomized.bloom_filter import BloomFilter, measured_false_positive_rate


def test_no_false_negatives():
    bloom = BloomFilter(256, 3, seed=5300)
    items = ["a", "b", "c", "d"]
    for item in items:
        bloom.add(item)
    assert all(bloom.check(item) for item in items)


def test_false_positive_rate_is_between_zero_and_one():
    rate = measured_false_positive_rate(
        [f"in-{i}" for i in range(40)],
        [f"out-{i}" for i in range(80)],
        m_bits=128,
        k_hashes=3,
        seed=5300,
    )
    assert 0.0 <= rate <= 1.0


def test_theoretical_fp_drops_when_the_array_grows():
    small = BloomFilter(64, 3)
    large = BloomFilter(512, 3)
    for i in range(20):
        small.add(str(i))
        large.add(str(i))
    assert large.theoretical_fp() < small.theoretical_fp()
