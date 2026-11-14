from collections.abc import Sequence

import pytest
from hypothesis import given
from hypothesis import strategies as st

from engine.curriculum import CycleError, find_cycle, topological_order
from engine.curriculum.graph import Prerequisites


@st.composite
def dags(draw: st.DrawFn) -> dict[str, list[str]]:
    """Random DAGs: nodes are shuffled, edges only point from later to earlier."""
    n = draw(st.integers(min_value=0, max_value=12))
    names = draw(st.permutations([f"n{i}" for i in range(n)]))
    prerequisites: dict[str, list[str]] = {}
    for i, name in enumerate(names):
        earlier = names[:i]
        prerequisites[name] = (
            draw(st.lists(st.sampled_from(earlier), unique=True)) if earlier else []
        )
    return prerequisites


def respects(order: Sequence[str], prerequisites: Prerequisites) -> bool:
    position = {item: i for i, item in enumerate(order)}
    return all(
        position[d] < position[item]
        for item, dependencies in prerequisites.items()
        for d in dependencies
    )


class TestTopologicalOrder:
    @given(dags())
    def test_respects_prerequisites(self, prerequisites: dict[str, list[str]]) -> None:
        order = topological_order(prerequisites)
        assert sorted(order) == sorted(prerequisites)
        assert respects(order, prerequisites)

    @given(dags())
    def test_is_deterministic(self, prerequisites: dict[str, list[str]]) -> None:
        assert topological_order(prerequisites) == topological_order(
            dict(reversed(prerequisites.items()))
        )

    def test_ties_are_broken_by_id(self) -> None:
        assert topological_order({"b": [], "a": [], "c": ["a"]}) == ("a", "b", "c")

    def test_cycle_path_is_reported(self) -> None:
        prerequisites = {"a": ["b"], "b": ["c"], "c": ["a"], "d": []}
        with pytest.raises(CycleError, match=r"a -> b -> c -> a"):
            topological_order(prerequisites)


class TestFindCycle:
    @given(dags())
    def test_dags_have_no_cycle(self, prerequisites: dict[str, list[str]]) -> None:
        assert find_cycle(prerequisites) is None

    @given(dags(), st.data())
    def test_back_edge_creates_a_reported_cycle(
        self, prerequisites: dict[str, list[str]], data: st.DataObject
    ) -> None:
        if not prerequisites:
            return
        # A self-loop is the simplest back edge
        node = data.draw(st.sampled_from(sorted(prerequisites)))
        prerequisites[node] = [*prerequisites[node], node]
        cycle = find_cycle(prerequisites)
        assert cycle is not None
        assert cycle[0] == cycle[-1]
        assert all(
            b in prerequisites[a] for a, b in zip(cycle, cycle[1:], strict=False)
        )

    def test_cycle_path_is_in_order(self) -> None:
        prerequisites = {"a": ["b"], "b": ["c"], "c": ["a"], "d": []}
        assert find_cycle(prerequisites) == ("a", "b", "c", "a")
