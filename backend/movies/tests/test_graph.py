import pytest

from movies.services.graph import (
    collect_ancestors,
    find_cycle_path,
    rewatch_order,
)

# IDs: 1 Iron Man, 2 First Avenger, 3 The Avengers, 4 Civil War,
#      5 Ragnarok, 6 Infinity War, 7 Endgame, 8 Doomsday
MCU = {
    1: [],
    2: [],
    3: [1, 2],
    4: [3],
    5: [],
    6: [4, 5],
    7: [6],
    8: [7],
}


def test_doomsday_needs_all_other_seven():
    assert collect_ancestors(8, MCU) == {1, 2, 3, 4, 5, 6, 7}


def test_civil_war_needs_iron_man_first_avenger_and_avengers():
    assert collect_ancestors(4, MCU) == {1, 2, 3}


def test_ragnarok_has_no_prerequisites():
    assert collect_ancestors(5, MCU) == set()


def test_target_is_not_included():
    assert 8 not in collect_ancestors(8, MCU)


def test_diamond_counts_shared_prerequisite_once():
    # A(1) needs B(2) and C(3); both need D(4)
    diamond = {1: [2, 3], 2: [4], 3: [4], 4: []}
    assert collect_ancestors(1, diamond) == {2, 3, 4}


def test_unknown_movie_returns_empty():
    assert collect_ancestors(999, MCU) == set()


# Sort keys as (release year, lowercase title), like the real app will use
KEYS = {
    1: (2008, "iron man"),
    2: (2011, "captain america: the first avenger"),
    3: (2012, "the avengers"),
    4: (2016, "captain america: civil war"),
    5: (2017, "thor: ragnarok"),
    6: (2018, "avengers: infinity war"),
    7: (2019, "avengers: endgame"),
    8: (2026, "avengers: doomsday"),
}


def assert_valid_order(order, prereqs):
    """Every movie appears once, and after all of its prerequisites."""
    assert len(order) == len(set(order))
    position = {movie_id: i for i, movie_id in enumerate(order)}
    for movie_id in order:
        for prereq_id in prereqs[movie_id]:
            assert position[prereq_id] < position[movie_id]


def test_order_doomsday_matches_pdf_sample():
    assert rewatch_order(8, MCU, KEYS) == [1, 2, 3, 4, 5, 6, 7]


def test_order_civil_war():
    order = rewatch_order(4, MCU, KEYS)
    assert order == [1, 2, 3]


def test_order_ragnarok_is_empty():
    assert rewatch_order(5, MCU, KEYS) == []


def test_order_excludes_target():
    assert 8 not in rewatch_order(8, MCU, KEYS)


def test_order_is_valid_for_every_movie():
    for target_id in MCU:
        order = rewatch_order(target_id, MCU, KEYS)
        assert set(order) == collect_ancestors(target_id, MCU)
        assert_valid_order(order, MCU)


def test_order_diamond_lists_shared_prerequisite_once():
    diamond = {1: [2, 3], 2: [4], 3: [4], 4: []}
    keys = {1: (4,), 2: (2,), 3: (3,), 4: (1,)}
    order = rewatch_order(1, diamond, keys)
    assert order == [4, 2, 3]
    assert_valid_order(order, diamond)


def test_order_long_chain_has_no_recursion_limit():
    chain = {1: []}
    for i in range(2, 2001):
        chain[i] = [i - 1]
    keys = {i: (i,) for i in chain}
    assert rewatch_order(2000, chain, keys) == list(range(1, 2000))


def test_order_raises_on_cycle():
    cyclic = {1: [2], 2: [1], 3: [1]}
    keys = {1: (1,), 2: (2,), 3: (3,)}
    with pytest.raises(ValueError):
        rewatch_order(3, cyclic, keys)


def test_cycle_endgame_as_prerequisite_of_iron_man():
    # The PDF example: must be rejected
    assert find_cycle_path(1, [7], MCU) == [1, 7, 6, 4, 3, 1]


def test_cycle_movie_cannot_depend_on_itself():
    assert find_cycle_path(3, [3], MCU) == [3, 3]


def test_cycle_two_movies_depending_on_each_other():
    graph = {1: [], 2: [1]}  # 2 already needs 1
    assert find_cycle_path(1, [2], graph) == [1, 2, 1]


def test_valid_changes_return_none():
    # Doomsday can also need Iron Man; Iron Man can need Ragnarok
    assert find_cycle_path(8, [1], MCU) is None
    assert find_cycle_path(1, [5], MCU) is None


def test_clearing_or_keeping_prerequisites_is_safe():
    assert find_cycle_path(3, [], MCU) is None
    assert find_cycle_path(3, [1, 2], MCU) is None  # same as today


def test_shared_ancestor_is_not_a_false_cycle():
    # 2 and 3 both need 4, but neither needs 1
    graph = {1: [], 2: [4], 3: [4], 4: []}
    assert find_cycle_path(1, [2, 3], graph) is None


def test_cycle_detection_on_long_chain_has_no_recursion_limit():
    chain = {1: []}
    for i in range(2, 2001):
        chain[i] = [i - 1]
    path = find_cycle_path(1, [2000], chain)
    assert path is not None
    assert path[0] == 1 and path[-1] == 1
    assert len(path) == 2001
