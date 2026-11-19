from movies.models import Movie, MoviePrerequisite


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