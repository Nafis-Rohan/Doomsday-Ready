# Create your models here.
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.functions import Lower


class Cinema(models.Model):
    name = models.CharField(max_length=200)
    # Bundle sizes sold for opening night, stored sorted ascending.
    # The API checks: 1-10 different sizes, each 1-500.
    bundle_sizes = ArrayField(models.PositiveSmallIntegerField(), size=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(Lower("name"), name="cinema_name_unique_ci"),
        ]

    def __str__(self):
        return self.name
