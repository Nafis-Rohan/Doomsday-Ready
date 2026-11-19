from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from cinemas.models import Cinema
from movies.models import Movie


@pytest.fixture
def api():
    """A client for making API requests."""
    return APIClient()


@pytest.fixture
def seeded(db):
    """The 8 MCU movies and 4 cinemas from the assessment."""
    call_command("seed", stdout=StringIO())


@pytest.fixture
def movie_ids(seeded):
    """Movie title -> id, e.g. movie_ids["Iron Man"]."""
    return {movie.title: movie.id for movie in Movie.objects.all()}


@pytest.fixture
def cinema_ids(seeded):
    """Cinema name -> id, e.g. cinema_ids["Starlight Cinema"]."""
    return {cinema.name: cinema.id for cinema in Cinema.objects.all()}
