from rest_framework import serializers

from .models import Movie


class PrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title"]


class MovieSerializer(serializers.ModelSerializer):
    """How a movie looks in API responses."""

    releaseYear = serializers.IntegerField(source="release_year")
    runtimeMinutes = serializers.IntegerField(source="runtime_minutes")
    prerequisites = PrerequisiteSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "releaseYear",
            "runtimeMinutes",
            "watched",
            "prerequisites",
            "createdAt",
            "updatedAt",
        ]