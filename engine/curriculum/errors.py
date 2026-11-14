class CurriculumError(Exception):
    """A curriculum is malformed. The message says exactly what and where."""


class CycleError(CurriculumError):
    """The prerequisite graph contains a cycle."""

    def __init__(self, cycle: tuple[str, ...]) -> None:
        self.cycle = cycle
        super().__init__("Prerequisite cycle: " + " -> ".join(cycle))
