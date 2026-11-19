# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie
from .serializers import MovieSerializer
from .services.graph import rewatch_order
from .services.movie_service import load_prereq_graph


class MovieListView(APIView):
    def get(self, request):
        movies = Movie.objects.prefetch_related("prerequisites")
        return Response(MovieSerializer(movies, many=True).data)


class RewatchOrderView(APIView):
    def get(self, request, pk):
        target = get_object_or_404(Movie, pk=pk)

        graph = load_prereq_graph()
        movies = {movie.id: movie for movie in Movie.objects.all()}
        sort_keys = {
            movie.id: (movie.release_year, movie.title.lower())
            for movie in movies.values()
        }

        order = [movies[i] for i in rewatch_order(target.id, graph, sort_keys)]
        watched_count = sum(1 for movie in order if movie.watched)
        remaining_minutes = sum(
            movie.runtime_minutes for movie in order if not movie.watched
        )

        return Response(
            {
                "target": {"id": target.id, "title": target.title},
                "order": [
                    {
                        "id": movie.id,
                        "title": movie.title,
                        "releaseYear": movie.release_year,
                        "runtimeMinutes": movie.runtime_minutes,
                        "watched": movie.watched,
                    }
                    for movie in order
                ],
                "totalCount": len(order),
                "watchedCount": watched_count,
                "unwatchedCount": len(order) - watched_count,
                "remainingRuntimeMinutes": remaining_minutes,
            }
        )