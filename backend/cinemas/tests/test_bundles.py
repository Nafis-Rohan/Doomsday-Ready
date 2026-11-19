import random
from itertools import product

from cinemas.services.bundles import min_bundles


def total_bundles(result):
    return sum(result.values())


def total_seats(result):
    return sum(size * count for size, count in result.items())


def brute_force_fewest(sizes, group_size):
    """Try every combination of counts. Slow, so only for tiny cases."""
    best = None
    ranges = [range(group_size // size + 1) for size in sizes]
    for counts in product(*ranges):
        if sum(c * s for c, s in zip(counts, sizes, strict=True)) == group_size:
            total = sum(counts)
            if best is None or total < best:
                best = total
    return best


# --- The four examples from the PDF ---


def test_pdf_1_3_4_for_6():
    assert min_bundles([1, 3, 4], 6) == {3: 2}


def test_pdf_2_5_for_11():
    assert min_bundles([2, 5], 11) == {5: 1, 2: 3}


def test_pdf_6_9_20_for_44():
    assert min_bundles([6, 9, 20], 44) == {20: 1, 9: 2, 6: 1}


def test_pdf_4_6_for_7_is_not_possible():
    assert min_bundles([4, 6], 7) is None


# --- Edge cases ---


def test_single_size_that_divides_exactly():
    assert min_bundles([5], 10) == {5: 2}


def test_single_size_that_does_not_divide():
    assert min_bundles([5], 7) is None


def test_size_one_makes_every_group_possible():
    for group_size in range(1, 51):
        result = min_bundles([1, 7], group_size)
        assert result is not None
        assert total_seats(result) == group_size


def test_group_smaller_than_every_bundle_is_not_possible():
    assert min_bundles([5, 10], 3) is None


def test_largest_allowed_inputs():
    # 10,000 seats with a 500-seat bundle: 20 bundles
    assert min_bundles([7, 500], 10_000) == {500: 20}


# --- Compare against a slow brute-force solver ---


def test_matches_brute_force_on_random_small_cases():
    rng = random.Random(42)
    for _ in range(300):
        sizes = rng.sample(range(1, 13), rng.randint(1, 3))
        group_size = rng.randint(1, 40)
        result = min_bundles(sizes, group_size)
        expected = brute_force_fewest(sizes, group_size)

        if expected is None:
            assert result is None
        else:
            assert result is not None
            assert total_bundles(result) == expected
            assert total_seats(result) == group_size
            assert set(result) <= set(sizes)
