import heapq
from collections import deque

Prereqs = dict[int, list[int]]


""" collect_ancestors """


def collect_ancestors(target_id: int, prereqs: Prereqs) -> set[int]:

    visited: set[int] = set()
    queue = deque(prereqs.get(target_id, []))

    while queue:
        movie_id = queue.popleft()
        if movie_id in visited:
            continue
        visited.add(movie_id)
        queue.extend(prereqs.get(movie_id, []))

    return visited


""" rewatch_order """


def rewatch_order(
    target_id: int,
    prereqs: Prereqs,
    sort_keys: dict[int, tuple],
) -> list[int]:
    ancestors = collect_ancestors(target_id, prereqs)

    remaining = {m: len(set(prereqs.get(m, []))) for m in ancestors}

    needed_by: dict[int, list[int]] = {m: [] for m in ancestors}
    for movie_id in ancestors:
        for prereq_id in set(prereqs.get(movie_id, [])):
            needed_by[prereq_id].append(movie_id)

    ready = [(sort_keys[m], m) for m, count in remaining.items() if count == 0]
    heapq.heapify(ready)

    order: list[int] = []
    while ready:
        _, movie_id = heapq.heappop(ready)
        order.append(movie_id)
        for dependent in needed_by[movie_id]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heapq.heappush(ready, (sort_keys[dependent], dependent))

    if len(order) != len(ancestors):
        raise ValueError("Cycle detected in movie prerequisites")

    return order


""" find_cycle_path """


def find_cycle_path(
    movie_id: int,
    new_prereq_ids: list[int],
    prereqs: Prereqs,
) -> list[int] | None:

    for start in sorted(set(new_prereq_ids)):
        if start == movie_id:
            return [movie_id, movie_id]  # depends on itself

        parent: dict[int, int | None] = {start: None}
        queue = deque([start])

        while queue:
            current = queue.popleft()
            for next_id in prereqs.get(current, []):
                if next_id in parent:
                    continue
                parent[next_id] = current
                if next_id == movie_id:
                    path = []
                    node: int | None = next_id
                    while node is not None:
                        path.append(node)
                        node = parent[node]
                    path.reverse()
                    return [movie_id] + path
                queue.append(next_id)

    return None
