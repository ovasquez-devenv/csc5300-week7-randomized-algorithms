"""Tests for the Bloom filter."""

import os
import subprocess
import sys

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


def test_same_seed_gives_same_bits_in_a_new_python_process():
    code = (
        "from src.randomized.bloom_filter import BloomFilter\n"
        "b = BloomFilter(128, 3, seed=5300)\n"
        "[b.add(f'in-{i}') for i in range(20)]\n"
        "print(bytes(b.bits).hex())\n"
    )
    outputs = set()
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONPATH=".")
        result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True)
        outputs.add(result.stdout)
    assert len(outputs) == 1
