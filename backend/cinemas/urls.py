from django.urls import path

from . import views

urlpatterns = [
    path("cinemas", views.CinemaListView.as_view(), name="cinema-list"),
    path("cinemas/<int:pk>", views.CinemaDetailView.as_view(), name="cinema-detail"),
    path(
        "cinemas/<int:pk>/booking",
        views.BookingQuoteView.as_view(),
        name="cinema-booking",
    ),
]
