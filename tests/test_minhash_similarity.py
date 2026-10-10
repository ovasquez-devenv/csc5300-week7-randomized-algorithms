"""Tests for MinHash Jaccard estimates."""

import os
import subprocess
import sys

from src.randomized.minhash_similarity import estimate_jaccard, estimation_error, jaccard


def test_identical_sets():
    tokens = ["red", "blue", "green"]
    assert jaccard(tokens, tokens) == 1.0
    assert estimate_jaccard(tokens, tokens, k=32, seed=5300) == 1.0


def test_disjoint_sets_have_low_estimate():
    left = [f"a{i}" for i in range(30)]
    right = [f"b{i}" for i in range(30)]
    assert jaccard(left, right) == 0.0
    assert estimate_jaccard(left, right, k=64, seed=5300) < 0.2


def test_error_is_a_nonnegative_gap():
    left = ["cat", "dog", "fish", "bird"]
    right = ["dog", "fish", "horse"]
    assert estimation_error(left, right, k=16, seed=2) >= 0.0


def test_same_seed_gives_same_estimate_in_a_new_python_process():
    code = (
        "from src.randomized.minhash_similarity import estimate_jaccard\n"
        "print(estimate_jaccard(['rent', 'unit', 'lease'], ['lease', 'unit', 'repair'], 32, 5300))\n"
    )
    outputs = set()
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONPATH=".")
        result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True)
        outputs.add(result.stdout)
    assert len(outputs) == 1
