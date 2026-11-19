from django.urls import path

from . import views

urlpatterns = [
    path("movies", views.MovieListView.as_view(), name="movie-list"),
    path("movies/<int:pk>", views.MovieDetailView.as_view(), name="movie-detail"),
    path(
        "movies/<int:pk>/rewatch-order",
        views.RewatchOrderView.as_view(),
        name="movie-rewatch-order",
    ),
]
