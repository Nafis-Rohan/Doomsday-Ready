from django.db import transaction
from django.db.models.functions import Lower

from cinemas.models import Cinema
from core.exceptions import DuplicateName


@transaction.atomic
def create_cinemas(items: list[dict]) -> list[Cinema]:
    """Create one or more cinemas at once. All of them are saved, or none."""
    lowered = [item["name"].lower() for item in items]
    if len(set(lowered)) != len(lowered):
        raise DuplicateName(
            message="The request contains the same name more than once."
        )

    taken = list(
        Cinema.objects.annotate(lower_name=Lower("name"))
        .filter(lower_name__in=lowered)
        .values_list("name", flat=True)
    )
    if taken:
        raise DuplicateName(details={"names": taken})

    return Cinema.objects.bulk_create(
        Cinema(name=item["name"], bundle_sizes=item["bundle_sizes"]) for item in items
    )
