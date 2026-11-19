from django.db import connection, transaction
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from core.exceptions import CircularDependency, DuplicateTitle, UnknownPrerequisite
from movies.models import Movie, MoviePrerequisite

from .graph import find_any_cycle, find_cycle_path

# Any constant number works. Every write that changes the graph takes this
# lock first, so two requests can never both pass the cycle check and then
# together create a loop.
GRAPH_LOCK_ID = 727001


def load_prereq_graph() -> dict[int, list[int]]:
    """Read the whole prerequisite graph from the database.

    Returns {movie_id: [ids of movies to watch first]}, in the shape the
    functions in graph.py expect. Two queries, however many movies exist.
    """
    graph: dict[int, list[int]] = {
        movie_id: [] for movie_id in Movie.objects.values_list("id", flat=True)
    }
    links = MoviePrerequisite.objects.values_list("movie_id", "prerequisite_id")
    for movie_id, prereq_id in links:
        graph[movie_id].append(prereq_id)
    return graph


def lock_graph() -> None:
    """Wait for our turn to change the graph (released when the transaction ends)."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [GRAPH_LOCK_ID])


def resolve_prerequisites(refs: list[int | str]) -> list[int]:
    """Turn a list of movie ids and/or titles into a list of movie ids."""
    ids = {ref for ref in refs if isinstance(ref, int)}
    lowered_titles = {ref.lower() for ref in refs if isinstance(ref, str)}

    by_id = {m.id: m for m in Movie.objects.filter(id__in=ids)}
    by_title = {
        m.title.lower(): m
        for m in Movie.objects.annotate(lower_title=Lower("title")).filter(
            lower_title__in=lowered_titles
        )
    }

    resolved: list[int] = []
    unknown = []
    for ref in refs:
        movie = by_id.get(ref) if isinstance(ref, int) else by_title.get(ref.lower())
        if movie is None:
            unknown.append(ref)
        elif movie.id not in resolved:
            resolved.append(movie.id)

    if unknown:
        raise UnknownPrerequisite(
            message="Some prerequisites do not match any existing movie.",
            details={"unknown": unknown},
        )
    return resolved


def raise_cycle_error(cycle: list[int]) -> None:
    """Turn a loop (list of movie ids) into a 409 CIRCULAR_DEPENDENCY error."""
    titles = dict(Movie.objects.filter(id__in=cycle).values_list("id", "title"))
    names = [titles[movie_id] for movie_id in cycle]
    if len(cycle) == 2:
        message = f"'{names[0]}' cannot depend on itself."
    else:
        message = (
            f"'{names[0]}' cannot depend on '{names[1]}' because "
            f"'{names[1]}' already depends on '{names[0]}', "
            "directly or through other movies."
        )
    raise CircularDependency(message=message, details={"cycle": names})


def ensure_no_cycle(movie: Movie, prereq_ids: list[int]) -> None:
    """Raise CircularDependency if these prerequisites would create a loop."""
    cycle = find_cycle_path(movie.id, prereq_ids, load_prereq_graph())
    if cycle is not None:
        raise_cycle_error(cycle)


@transaction.atomic
def update_movie(movie_id: int, data: dict) -> Movie:
    """Apply a partial update. `prerequisites`, if present, replaces the set."""
    lock_graph()
    movie = get_object_or_404(Movie, pk=movie_id)

    data = dict(data)
    refs = data.pop("prerequisites", None)

    new_title = data.get("title")
    if new_title is not None:
        taken = Movie.objects.filter(title__iexact=new_title).exclude(pk=movie.pk)
        if taken.exists():
            raise DuplicateTitle()

    prereq_ids = None
    if refs is not None:
        prereq_ids = resolve_prerequisites(refs)
        ensure_no_cycle(movie, prereq_ids)

    for field, value in data.items():
        setattr(movie, field, value)
    movie.save()

    if prereq_ids is not None:
        MoviePrerequisite.objects.filter(movie=movie).delete()
        MoviePrerequisite.objects.bulk_create(
            MoviePrerequisite(movie=movie, prerequisite_id=pid) for pid in prereq_ids
        )

    return movie


@transaction.atomic
def create_movies(items: list[dict]) -> list[Movie]:
    """Create one or more movies at once. All of them are saved, or none.

    A prerequisite given as a title can point at a movie created in the same
    request, so a whole franchise can be created in one call.
    """
    lock_graph()

    lowered = [item["title"].lower() for item in items]
    if len(set(lowered)) != len(lowered):
        raise DuplicateTitle(
            message="The request contains the same title more than once."
        )
    taken = list(
        Movie.objects.annotate(lower_title=Lower("title"))
        .filter(lower_title__in=lowered)
        .values_list("title", flat=True)
    )
    if taken:
        raise DuplicateTitle(details={"titles": taken})

    movies = Movie.objects.bulk_create(
        Movie(
            title=item["title"],
            release_year=item["release_year"],
            runtime_minutes=item["runtime_minutes"],
            watched=item.get("watched", False),
        )
        for item in items
    )

    # The new movies exist inside this transaction now, so titles that point
    # at other new movies resolve too.
    graph = load_prereq_graph()
    links = []
    for movie, item in zip(movies, items, strict=True):
        prereq_ids = resolve_prerequisites(item.get("prerequisites", []))
        graph[movie.id] = prereq_ids
        links.extend(
            MoviePrerequisite(movie=movie, prerequisite_id=pid) for pid in prereq_ids
        )

    # The old graph had no loops, so any loop found now involves a new movie.
    cycle = find_any_cycle(graph)
    if cycle is not None:
        raise_cycle_error(cycle)

    MoviePrerequisite.objects.bulk_create(links)
    return movies
