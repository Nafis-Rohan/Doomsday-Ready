from rest_framework import serializers

from .models import Cinema


class CinemaSerializer(serializers.ModelSerializer):
    """How a cinema looks in API responses."""

    bundleSizes = serializers.ListField(
        source="bundle_sizes", child=serializers.IntegerField(), read_only=True
    )
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Cinema
        fields = ["id", "name", "bundleSizes", "createdAt", "updatedAt"]


class CinemaWriteSerializer(serializers.Serializer):
    """Checks the input when creating a cinema."""

    name = serializers.CharField(max_length=200)
    bundleSizes = serializers.ListField(
        source="bundle_sizes",
        child=serializers.IntegerField(min_value=1, max_value=500),
        min_length=1,
        max_length=10,
    )

    def validate_bundleSizes(self, value):
        if len(set(value)) != len(value):
            raise serializers.ValidationError("Bundle sizes must all be different.")
        return sorted(value)
