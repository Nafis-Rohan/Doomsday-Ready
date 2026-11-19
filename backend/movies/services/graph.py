from collections import deque

Prereqs = dict[int, list[int]]


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