from rest_framework import serializers

from .models import Movie


class PrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title"]


class MovieSerializer(serializers.ModelSerializer):
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


class PrerequisiteRefField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, bool) or not isinstance(data, int | str):
            raise serializers.ValidationError(
                "Use a movie id (integer) or a movie title (string)."
            )
        if isinstance(data, str):
            data = data.strip()
            if not data:
                raise serializers.ValidationError("A title must not be empty.")
        return data

    def to_representation(self, value):
        return value


class MovieWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    releaseYear = serializers.IntegerField(
        source="release_year", min_value=1900, max_value=2100
    )
    runtimeMinutes = serializers.IntegerField(
        source="runtime_minutes", min_value=1, max_value=300
    )
    watched = serializers.BooleanField(required=False, default=False)
    prerequisites = serializers.ListField(child=PrerequisiteRefField(), required=False)
