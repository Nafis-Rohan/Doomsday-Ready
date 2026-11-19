import pytest

pytestmark = pytest.mark.django_db

MOVIES_URL = "/api/movies"


def titles(order):
    return [movie["title"] for movie in order]


# --- List and detail ---


def test_list_returns_all_movies_in_release_order(api, seeded):
    response = api.get(MOVIES_URL)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 8
    assert body[0]["title"] == "Iron Man"
    assert body[-1]["title"] == "Avengers: Doomsday"


def test_movie_shape_uses_camel_case_and_lists_prerequisites(api, movie_ids):
    response = api.get(f"{MOVIES_URL}/{movie_ids['Avengers: Doomsday']}")

    assert response.status_code == 200
    body = response.json()
    assert body["releaseYear"] == 2026
    assert body["runtimeMinutes"] == 150
    assert body["watched"] is False
    assert body["prerequisites"] == [
        {"id": movie_ids["Avengers: Endgame"], "title": "Avengers: Endgame"}
    ]


def test_missing_movie_returns_404_in_standard_error_shape(api, seeded):
    response = api.get(f"{MOVIES_URL}/99999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# --- Rewatch order (the PDF's expected results) ---


def test_rewatch_order_for_doomsday(api, movie_ids):
    response = api.get(f"{MOVIES_URL}/{movie_ids['Avengers: Doomsday']}/rewatch-order")

    assert response.status_code == 200
    body = response.json()
    assert titles(body["order"]) == [
        "Iron Man",
        "Captain America: The First Avenger",
        "The Avengers",
        "Captain America: Civil War",
        "Thor: Ragnarok",
        "Avengers: Infinity War",
        "Avengers: Endgame",
    ]
    assert body["target"]["title"] == "Avengers: Doomsday"
    assert body["totalCount"] == 7
    assert body["watchedCount"] == 0
    assert body["unwatchedCount"] == 7
    assert body["remainingRuntimeMinutes"] == 1000


def test_rewatch_order_for_civil_war(api, movie_ids):
    response = api.get(
        f"{MOVIES_URL}/{movie_ids['Captain America: Civil War']}/rewatch-order"
    )

    assert response.status_code == 200
    assert titles(response.json()["order"]) == [
        "Iron Man",
        "Captain America: The First Avenger",
        "The Avengers",
    ]


def test_rewatch_order_for_ragnarok_is_empty(api, movie_ids):
    response = api.get(f"{MOVIES_URL}/{movie_ids['Thor: Ragnarok']}/rewatch-order")

    assert response.status_code == 200
    body = response.json()
    assert body["order"] == []
    assert body["totalCount"] == 0
    assert body["watchedCount"] == 0
    assert body["remainingRuntimeMinutes"] == 0


def test_rewatch_order_does_not_include_the_target(api, movie_ids):
    target_id = movie_ids["Avengers: Doomsday"]
    response = api.get(f"{MOVIES_URL}/{target_id}/rewatch-order")

    ids = [movie["id"] for movie in response.json()["order"]]
    assert target_id not in ids


def test_rewatch_order_counts_watched_and_remaining_runtime(api, movie_ids):
    # Mark Iron Man (126 min) and The First Avenger (124 min) as watched
    for title in ["Iron Man", "Captain America: The First Avenger"]:
        api.patch(f"{MOVIES_URL}/{movie_ids[title]}", {"watched": True}, format="json")

    response = api.get(f"{MOVIES_URL}/{movie_ids['Avengers: Doomsday']}/rewatch-order")

    body = response.json()
    assert body["totalCount"] == 7
    assert body["watchedCount"] == 2
    assert body["unwatchedCount"] == 5
    assert body["remainingRuntimeMinutes"] == 1000 - 126 - 124
    watched_flags = {m["title"]: m["watched"] for m in body["order"]}
    assert watched_flags["Iron Man"] is True
    assert watched_flags["The Avengers"] is False


def test_rewatch_order_for_missing_movie_returns_404(api, seeded):
    response = api.get(f"{MOVIES_URL}/99999/rewatch-order")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# --- PATCH ---


def patch(api, movie_id, body):
    return api.patch(f"{MOVIES_URL}/{movie_id}", body, format="json")


def prereq_titles(body):
    return sorted(p["title"] for p in body["prerequisites"])


def test_patch_marks_movie_as_watched(api, movie_ids):
    movie_id = movie_ids["Iron Man"]

    response = patch(api, movie_id, {"watched": True})

    assert response.status_code == 200
    assert response.json()["watched"] is True
    assert api.get(f"{MOVIES_URL}/{movie_id}").json()["watched"] is True


def test_patch_can_change_title_year_and_runtime(api, movie_ids):
    response = patch(
        api,
        movie_ids["Thor: Ragnarok"],
        {"title": "Thor 3", "releaseYear": 2018, "runtimeMinutes": 131},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["title"] == "Thor 3"
    assert body["releaseYear"] == 2018
    assert body["runtimeMinutes"] == 131


def test_patch_replaces_prerequisites_by_id_or_title(api, movie_ids):
    ragnarok = movie_ids["Thor: Ragnarok"]

    by_id = patch(api, ragnarok, {"prerequisites": [movie_ids["Iron Man"]]})
    assert prereq_titles(by_id.json()) == ["Iron Man"]

    by_title = patch(
        api, ragnarok, {"prerequisites": ["Captain America: The First Avenger"]}
    )
    assert prereq_titles(by_title.json()) == ["Captain America: The First Avenger"]


def test_patch_empty_list_clears_prerequisites(api, movie_ids):
    response = patch(api, movie_ids["The Avengers"], {"prerequisites": []})

    assert response.status_code == 200
    assert response.json()["prerequisites"] == []


def test_patch_adding_a_valid_prerequisite_is_accepted(api, movie_ids):
    response = patch(
        api,
        movie_ids["Avengers: Doomsday"],
        {
            "prerequisites": [
                movie_ids["Avengers: Endgame"],
                movie_ids["Thor: Ragnarok"],
            ]
        },
    )

    assert response.status_code == 200
    assert prereq_titles(response.json()) == ["Avengers: Endgame", "Thor: Ragnarok"]


def test_patch_endgame_as_prerequisite_of_iron_man_is_rejected(api, movie_ids):
    """The example from the assessment."""
    iron_man = movie_ids["Iron Man"]

    response = patch(api, iron_man, {"prerequisites": [movie_ids["Avengers: Endgame"]]})

    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "CIRCULAR_DEPENDENCY"
    cycle = error["details"]["cycle"]
    assert cycle[0] == "Iron Man" and cycle[-1] == "Iron Man"
    assert "Avengers: Endgame" in cycle

    # Nothing was saved
    assert api.get(f"{MOVIES_URL}/{iron_man}").json()["prerequisites"] == []


def test_patch_indirect_cycle_leaves_prerequisites_unchanged(api, movie_ids):
    avengers = movie_ids["The Avengers"]

    response = patch(
        api, avengers, {"prerequisites": [movie_ids["Captain America: Civil War"]]}
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CIRCULAR_DEPENDENCY"
    unchanged = api.get(f"{MOVIES_URL}/{avengers}").json()
    assert prereq_titles(unchanged) == [
        "Captain America: The First Avenger",
        "Iron Man",
    ]


def test_patch_movie_cannot_depend_on_itself(api, movie_ids):
    iron_man = movie_ids["Iron Man"]

    response = patch(api, iron_man, {"prerequisites": [iron_man]})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CIRCULAR_DEPENDENCY"


def test_patch_unknown_prerequisite_is_a_bad_request(api, movie_ids):
    response = patch(api, movie_ids["Iron Man"], {"prerequisites": [99999]})

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "UNKNOWN_PREREQUISITE"
    assert error["details"]["unknown"] == [99999]


def test_patch_duplicate_title_is_a_conflict_ignoring_case(api, movie_ids):
    response = patch(api, movie_ids["Thor: Ragnarok"], {"title": "iron man"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_TITLE"


def test_patch_keeping_the_same_title_is_fine(api, movie_ids):
    response = patch(api, movie_ids["Iron Man"], {"title": "Iron Man", "watched": True})

    assert response.status_code == 200


@pytest.mark.parametrize(
    ("runtime", "expected_status"),
    [(0, 400), (1, 200), (300, 200), (301, 400)],
)
def test_patch_runtime_must_be_between_1_and_300(
    api, movie_ids, runtime, expected_status
):
    response = patch(api, movie_ids["Iron Man"], {"runtimeMinutes": runtime})

    assert response.status_code == expected_status
    if expected_status == 400:
        error = response.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert "runtimeMinutes" in error["details"]


def test_patch_missing_movie_returns_404(api, seeded):
    response = patch(api, 99999, {"watched": True})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# --- POST ---


def new_movie(title, prerequisites=None, runtime=100, year=2020):
    body = {"title": title, "releaseYear": year, "runtimeMinutes": runtime}
    if prerequisites is not None:
        body["prerequisites"] = prerequisites
    return body


def post(api, body):
    return api.post(MOVIES_URL, body, format="json")


def movie_count(api):
    return len(api.get(MOVIES_URL).json())


def test_post_creates_a_movie_with_defaults(api, seeded):
    response = post(api, new_movie("Black Panther", year=2018, runtime=134))

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Black Panther"
    assert body["releaseYear"] == 2018
    assert body["runtimeMinutes"] == 134
    assert body["watched"] is False
    assert body["prerequisites"] == []
    assert movie_count(api) == 9


def test_post_accepts_prerequisites_by_title_or_id(api, movie_ids):
    by_title = post(api, new_movie("Movie X", ["Iron Man"]))
    by_id = post(api, new_movie("Movie Y", [movie_ids["Thor: Ragnarok"]]))

    assert by_title.status_code == 201
    assert prereq_titles(by_title.json()) == ["Iron Man"]
    assert by_id.status_code == 201
    assert prereq_titles(by_id.json()) == ["Thor: Ragnarok"]


def test_post_batch_creates_movies_that_reference_each_other(api, seeded):
    body = [
        new_movie("Movie C", ["Movie B", "Iron Man"]),
        new_movie("Movie B", ["Movie A"]),
        new_movie("Movie A"),
    ]

    response = post(api, body)

    assert response.status_code == 201
    created = response.json()
    assert [m["title"] for m in created] == ["Movie C", "Movie B", "Movie A"]
    movie_c = next(m["id"] for m in created if m["title"] == "Movie C")
    order = api.get(f"{MOVIES_URL}/{movie_c}/rewatch-order").json()
    assert sorted(titles(order["order"])) == ["Iron Man", "Movie A", "Movie B"]


def test_post_duplicate_title_is_a_conflict_ignoring_case(api, seeded):
    response = post(api, new_movie("IRON MAN"))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_TITLE"
    assert movie_count(api) == 8


def test_post_same_title_twice_in_one_request_creates_nothing(api, seeded):
    response = post(api, [new_movie("Twin"), new_movie("twin")])

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_TITLE"
    assert movie_count(api) == 8


def test_post_movie_that_depends_on_itself_is_rejected(api, seeded):
    response = post(api, new_movie("Loop Movie", ["Loop Movie"]))

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CIRCULAR_DEPENDENCY"
    assert movie_count(api) == 8


def test_post_batch_with_a_loop_between_new_movies_creates_nothing(api, seeded):
    body = [new_movie("Movie A", ["Movie B"]), new_movie("Movie B", ["Movie A"])]

    response = post(api, body)

    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "CIRCULAR_DEPENDENCY"
    assert {"Movie A", "Movie B"} <= set(error["details"]["cycle"])
    assert movie_count(api) == 8


def test_post_batch_is_all_or_nothing(api, seeded):
    body = [new_movie("Good Movie"), new_movie("Bad Movie", ["No Such Movie"])]

    response = post(api, body)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNKNOWN_PREREQUISITE"
    assert movie_count(api) == 8


def test_post_unknown_prerequisite_is_a_bad_request(api, seeded):
    response = post(api, new_movie("Movie Z", [99999]))

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNKNOWN_PREREQUISITE"


def test_post_missing_required_fields_is_a_validation_error(api, seeded):
    response = post(api, {"title": "No Year Or Runtime"})

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "releaseYear" in error["details"]
    assert "runtimeMinutes" in error["details"]


def test_post_empty_list_is_rejected(api, seeded):
    response = post(api, [])

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    ("runtime", "expected_status"),
    [(0, 400), (1, 201), (300, 201), (301, 400)],
)
def test_post_runtime_must_be_between_1_and_300(api, seeded, runtime, expected_status):
    response = post(api, new_movie("Runtime Test", runtime=runtime))

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("year", "expected_status"),
    [(1899, 400), (1900, 201), (2100, 201), (2101, 400)],
)
def test_post_release_year_must_be_between_1900_and_2100(
    api, seeded, year, expected_status
):
    response = post(api, new_movie("Year Test", year=year))

    assert response.status_code == expected_status
