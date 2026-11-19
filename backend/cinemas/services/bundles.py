"""Pure booking helper for cinema bundles (no Django imports)."""


def min_bundles(sizes: list[int], group_size: int) -> dict[int, int] | None:
    """Return the fewest bundles that add up to exactly group_size seats.

    The result maps bundle size -> how many of that bundle to buy, ordered
    from the largest size to the smallest, e.g. {5: 1, 2: 3}. Returns None
    if no exact combination exists.

    Dynamic programming: fewest[s] is the minimum number of bundles that
    make exactly s seats. Any bundle size can be used as many times as needed.
    """
    options = sorted(set(sizes), reverse=True)

    unreachable = group_size + 1  # more bundles than could ever be needed
    fewest = [0] + [unreachable] * group_size
    last_used = [0] * (group_size + 1)  # the bundle that gave fewest[s]

    for seats in range(1, group_size + 1):
        for size in options:
            if size > seats:
                continue
            candidate = fewest[seats - size] + 1
            if candidate < fewest[seats]:
                fewest[seats] = candidate
                last_used[seats] = size

    if fewest[group_size] == unreachable:
        return None

    # Walk back from group_size, counting the bundle used at each step.
    counts: dict[int, int] = {}
    seats = group_size
    while seats > 0:
        size = last_used[seats]
        counts[size] = counts.get(size, 0) + 1
        seats -= size

    return dict(sorted(counts.items(), reverse=True))
