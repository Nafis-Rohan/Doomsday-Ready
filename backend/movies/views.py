from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie
from .serializers import MovieSerializer, MovieWriteSerializer
from .services.graph import rewatch_order
from .services.movie_service import create_movies, load_prereq_graph, update_movie


class MovieListView(APIView):
    def get(self, request):
        movies = Movie.objects.prefetch_related("prerequisites")
        return Response(MovieSerializer(movies, many=True).data)

    def post(self, request):
        # One movie ({...}) or several ([{...}, {...}])
        is_batch = isinstance(request.data, list)
        serializer = MovieWriteSerializer(
            data=request.data,
            many=is_batch,
            **({"allow_empty": False} if is_batch else {}),
        )
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data if is_batch else [serializer.validated_data]

        created = create_movies(items)

        by_id = {
            movie.id: movie
            for movie in Movie.objects.filter(
                id__in=[m.id for m in created]
            ).prefetch_related("prerequisites")
        }
        data = [MovieSerializer(by_id[m.id]).data for m in created]
        return Response(data if is_batch else data[0], status=status.HTTP_201_CREATED)


class MovieDetailView(APIView):
    def get(self, request, pk):
        queryset = Movie.objects.prefetch_related("prerequisites")
        movie = get_object_or_404(queryset, pk=pk)
        return Response(MovieSerializer(movie).data)

    def patch(self, request, pk):
        serializer = MovieWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        update_movie(pk, serializer.validated_data)

        movie = Movie.objects.prefetch_related("prerequisites").get(pk=pk)
        return Response(MovieSerializer(movie).data)


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
