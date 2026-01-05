import math

from umcp.eid import prime_pi, EIDCounts, eid_checksum, delta_kappa_eid


def test_prime_pi_basic_values():
    # primes <= 1: 0
    assert prime_pi(1) == 0
    # primes <= 2: {2}
    assert prime_pi(2) == 1
    # primes <= 10: {2,3,5,7}
    assert prime_pi(10) == 4
    # primes <= 30: {2,3,5,7,11,13,17,19,23,29}
    assert prime_pi(30) == 10


def test_eid_checksum_is_prime_weighted_and_deterministic():
    counts = [1, 2, 3]  # weights are primes [2,3,5]
    expected = 1 * 2 + 2 * 3 + 3 * 5  # 2 + 6 + 15 = 23
    assert eid_checksum(counts) == expected

    e = EIDCounts(counts=counts)
    assert e.mass == 6
    assert e.checksum() == expected


def test_delta_kappa_eid_mass_ratio():
    pre = EIDCounts(counts=[1, 1])    # mass 2
    post = EIDCounts(counts=[2, 1])   # mass 3
    dk = delta_kappa_eid(pre, post)
    assert math.isclose(dk, math.log(3.0 / 2.0), rel_tol=0.0, abs_tol=1e-12)
