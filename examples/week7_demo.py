"""Short smoke run of the Week 7 pieces.

Omar Vasquez, CSC 5300 Week 7.
"""

from src.randomized.bloom_filter import BloomFilter
from src.randomized.minhash_similarity import estimate_jaccard, jaccard
from src.randomized.montecarlo_primality import fermat_is_prime, miller_rabin_is_prime
from src.randomized.randomized_quicksort import deterministic_quicksort, randomized_quicksort
from src.randomized.randomized_selection import randomized_select
from src.randomized.week2_quicksort import quick_sort

data = [4, 1, 7, 3, 9, 2]
print("randomized", randomized_quicksort(data, seed=5300))
print("deterministic", deterministic_quicksort(data))
print("week2 copy", quick_sort(data))
print("median", randomized_select(data, len(data) // 2, seed=5300))
print("fermat 561", fermat_is_prime(561, k=5, seed=5300))
print("miller 561", miller_rabin_is_prime(561, k=5, seed=5300))
bloom = BloomFilter(64, 3, seed=5300)
bloom.add("lease")
print("bloom lease", bloom.check("lease"), "missing", bloom.check("missing"))
left = ["rent", "unit", "lease"]
right = ["lease", "unit", "repair"]
print("jaccard", round(jaccard(left, right), 3), "estimate", round(estimate_jaccard(left, right, 32, 5300), 3))
