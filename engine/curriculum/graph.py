"""Pure graph helpers over a prerequisite mapping ``item -> its prerequisites``."""

import heapq
from collections.abc import Mapping, Sequence

from engine.curriculum.errors import CycleError

type Prerequisites = Mapping[str, Sequence[str]]


def find_cycle(prerequisites: Prerequisites) -> tuple[str, ...] | None:
    """Return one cycle as a closed path (``("a", "b", "a")``), or ``None``.

    Edges pointing at nodes absent from ``prerequisites`` are ignored. Deterministic:
    nodes and edges are visited in sorted order.
    """
    white, grey, black = 0, 1, 2
    colour: dict[str, int] = dict.fromkeys(prerequisites, white)

    for root in sorted(prerequisites):
        if colour[root] != white:
            continue
        path: list[str] = [root]
        iterators = [iter(sorted(prerequisites[root]))]
        colour[root] = grey
        while iterators:
            for next_item in iterators[-1]:
                if next_item not in colour:
                    continue
                if colour[next_item] == grey:
                    return (*path[path.index(next_item) :], next_item)
                if colour[next_item] == white:
                    colour[next_item] = grey
                    path.append(next_item)
                    iterators.append(iter(sorted(prerequisites[next_item])))
                    break
            else:
                colour[path.pop()] = black
                iterators.pop()
    return None


def topological_order(prerequisites: Prerequisites) -> tuple[str, ...]:
    """Order items so each follows all of its prerequisites.

    Deterministic: among items that are ready, the smallest id goes first.
    Raises ``CycleError`` if the graph has a cycle.
    """
    remaining = {
        item: len(set(dependencies)) for item, dependencies in prerequisites.items()
    }
    dependants: dict[str, list[str]] = {item: [] for item in prerequisites}
    for item, dependencies in prerequisites.items():
        for dependency in set(dependencies):
            dependants[dependency].append(item)

    ready = [item for item, count in remaining.items() if count == 0]
    heapq.heapify(ready)
    result: list[str] = []
    while ready:
        item = heapq.heappop(ready)
        result.append(item)
        for dependant in dependants[item]:
            remaining[dependant] -= 1
            if remaining[dependant] == 0:
                heapq.heappush(ready, dependant)

    if len(result) != len(prerequisites):
        cycle = find_cycle(prerequisites)
        assert cycle is not None
        raise CycleError(cycle)
    return tuple(result)
