from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import InvalidGroupSize

from .models import Cinema
from .serializers import CinemaSerializer, CinemaWriteSerializer
from .services.bundles import min_bundles
from .services.cinema_service import create_cinemas

MIN_GROUP_SIZE = 1
MAX_GROUP_SIZE = 10_000


class CinemaListView(APIView):
    def get(self, request):
        return Response(CinemaSerializer(Cinema.objects.all(), many=True).data)

    def post(self, request):
        # One cinema ({...}) or several ([{...}, {...}])
        is_batch = isinstance(request.data, list)
        serializer = CinemaWriteSerializer(
            data=request.data,
            many=is_batch,
            **({"allow_empty": False} if is_batch else {}),
        )
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data if is_batch else [serializer.validated_data]

        created = create_cinemas(items)

        data = CinemaSerializer(created, many=True).data
        return Response(
            data if is_batch else data[0], status=status.HTTP_201_CREATED
        )


class CinemaDetailView(APIView):
    def get(self, request, pk):
        cinema = get_object_or_404(Cinema, pk=pk)
        return Response(CinemaSerializer(cinema).data)


class BookingQuoteView(APIView):
    def get(self, request, pk):
        cinema = get_object_or_404(Cinema, pk=pk)
        group_size = self._parse_group_size(request.query_params.get("groupSize"))

        counts = min_bundles(cinema.bundle_sizes, group_size)

        cinema_info = {
            "id": cinema.id,
            "name": cinema.name,
            "bundleSizes": cinema.bundle_sizes,
        }

        if counts is None:
            return Response(
                {
                    "cinema": cinema_info,
                    "groupSize": group_size,
                    "possible": False,
                    "totalBundles": None,
                    "bundles": [],
                    "message": (
                        f"No combination of bundles adds up to exactly "
                        f"{group_size} seats."
                    ),
                }
            )

        return Response(
            {
                "cinema": cinema_info,
                "groupSize": group_size,
                "possible": True,
                "totalBundles": sum(counts.values()),
                "bundles": [
                    {"size": size, "count": count} for size, count in counts.items()
                ],
            }
        )

    @staticmethod
    def _parse_group_size(raw: str | None) -> int:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            raise InvalidGroupSize() from None
        if not MIN_GROUP_SIZE <= value <= MAX_GROUP_SIZE:
            raise InvalidGroupSize()
        return value