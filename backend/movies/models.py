# Create your models here.
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower


class Movie(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.PositiveSmallIntegerField()
    runtime_minutes = models.PositiveSmallIntegerField()
    watched = models.BooleanField(default=False)
    prerequisites = models.ManyToManyField(
        "self",
        through="MoviePrerequisite",
        through_fields=("movie", "prerequisite"),
        symmetrical=False,
        related_name="required_by",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["release_year", "title"]
        constraints = [
            # "Iron Man" and "iron man" count as the same title
            models.UniqueConstraint(Lower("title"), name="movie_title_unique_ci"),
            models.CheckConstraint(
                condition=Q(runtime_minutes__gte=1, runtime_minutes__lte=300),
                name="movie_runtime_1_to_300",
            ),
        ]

    def __str__(self):
        return self.title


class MoviePrerequisite(models.Model):
    """One link: `movie` needs `prerequisite` to be watched first."""

    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="prerequisite_links"
    )
    prerequisite = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="dependent_links"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "prerequisite"],
                name="movie_prerequisite_unique_pair",
            ),
            # Database-level guard against a movie requiring itself
            models.CheckConstraint(
                condition=~Q(movie=F("prerequisite")),
                name="movie_prerequisite_not_self",
            ),
        ]

    def __str__(self):
        return f"{self.movie} needs {self.prerequisite}"
