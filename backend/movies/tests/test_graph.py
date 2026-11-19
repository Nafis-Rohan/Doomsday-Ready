from movies.services.graph import collect_ancestors

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