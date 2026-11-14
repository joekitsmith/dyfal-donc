import heapq
from collections.abc import Mapping, Sequence
from enum import Enum, auto

from engine.curriculum.errors import CurriculumError, CycleError

type Prerequisites = Mapping[str, Sequence[str]]


class _VisitState(Enum):
    UNVISITED = auto()
    IN_PROGRESS = auto()  # on the current depth-first path
    DONE = auto()  # fully explored, no cycle through it


def find_cycle(prerequisites: Prerequisites) -> tuple[str, ...] | None:
    """Return one cycle as a closed path (``("a", "b", "a")``), or ``None``.

    Edges pointing at nodes absent from ``prerequisites`` are ignored. Deterministic:
    nodes and edges are visited in sorted order.
    """
    state = dict.fromkeys(prerequisites, _VisitState.UNVISITED)

    for root in sorted(prerequisites):
        if state[root] != _VisitState.UNVISITED:
            continue
        path: list[str] = [root]
        iterators = [iter(sorted(prerequisites[root]))]
        state[root] = _VisitState.IN_PROGRESS
        while iterators:
            for next_item in iterators[-1]:
                if next_item not in state:
                    continue
                if state[next_item] == _VisitState.IN_PROGRESS:
                    return (*path[path.index(next_item) :], next_item)
                if state[next_item] == _VisitState.UNVISITED:
                    state[next_item] = _VisitState.IN_PROGRESS
                    path.append(next_item)
                    iterators.append(iter(sorted(prerequisites[next_item])))
                    break
            else:
                state[path.pop()] = _VisitState.DONE
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
        if cycle is None:
            raise CurriculumError(
                "could not order items, but no prerequisite cycle was found"
            )
        raise CycleError(cycle)
    return tuple(result)
