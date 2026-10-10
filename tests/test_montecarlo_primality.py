"""Tests for Fermat and Miller-Rabin."""

from src.randomized.montecarlo_primality import (
    CARMICHAEL,
    fermat_is_prime,
    miller_rabin_is_prime,
    trial_division_is_prime,
)


def test_small_primes_and_composites():
    for n in (2, 3, 5, 17, 97):
        assert trial_division_is_prime(n)
        assert miller_rabin_is_prime(n, k=5, seed=5300)
        assert fermat_is_prime(n, k=5, seed=5300)
    for n in (1, 4, 9, 15, 21, 25):
        assert not trial_division_is_prime(n)
        assert not miller_rabin_is_prime(n, k=8, seed=5300)


def test_carmichael_fools_fermat_more_often_than_miller_rabin():
    fermat_passes = 0
    miller_passes = 0
    for n in CARMICHAEL:
        assert not trial_division_is_prime(n)
        if fermat_is_prime(n, k=5, seed=5300):
            fermat_passes += 1
        if miller_rabin_is_prime(n, k=5, seed=5300):
            miller_passes += 1
    assert fermat_passes > miller_passes
