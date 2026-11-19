from django.core.management.base import BaseCommand
from django.db import transaction

from cinemas.models import Cinema
from movies.models import Movie, MoviePrerequisite

# (title, release year, runtime in minutes, titles of prerequisites)
# Sample data from the assessment; Doomsday's runtime is a placeholder.
MOVIES = [
    ("Iron Man", 2008, 126, []),
    ("Captain America: The First Avenger", 2011, 124, []),
    (
        "The Avengers",
        2012,
        143,
        ["Iron Man", "Captain America: The First Avenger"],
    ),
    ("Captain America: Civil War", 2016, 147, ["The Avengers"]),
    ("Thor: Ragnarok", 2017, 130, []),
    (
        "Avengers: Infinity War",
        2018,
        149,
        ["Captain America: Civil War", "Thor: Ragnarok"],
    ),
    ("Avengers: Endgame", 2019, 181, ["Avengers: Infinity War"]),
    ("Avengers: Doomsday", 2026, 150, ["Avengers: Endgame"]),
]

# One cinema per example row in the assessment's booking table.
CINEMAS = [
    ("Starlight Cinema", [1, 3, 4]),  # group of 6  -> 3 x 2
    ("Blockbuster Cinema", [2, 5]),  # group of 11 -> 5 x 1, 2 x 3
    ("Grand Cineplex", [6, 9, 20]),  # group of 44 -> 20 x 1, 9 x 2, 6 x 1
    ("Metro Screens", [4, 6]),  # group of 7  -> not possible
]


class Command(BaseCommand):
    help = "Load the sample movies and cinemas. Safe to run more than once."

    @transaction.atomic
    def handle(self, *args, **options):
        by_title = {}
        for title, year, runtime, _prereqs in MOVIES:
            movie, _created = Movie.objects.get_or_create(
                title=title,
                defaults={"release_year": year, "runtime_minutes": runtime},
            )
            by_title[title] = movie

        for title, _year, _runtime, prereq_titles in MOVIES:
            for prereq_title in prereq_titles:
                MoviePrerequisite.objects.get_or_create(
                    movie=by_title[title],
                    prerequisite=by_title[prereq_title],
                )

        for name, sizes in CINEMAS:
            Cinema.objects.get_or_create(
                name=name,
                defaults={"bundle_sizes": sorted(sizes)},
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Movie.objects.count()} movies, "
                f"{MoviePrerequisite.objects.count()} prerequisite links "
                f"and {Cinema.objects.count()} cinemas."
            )
        )
