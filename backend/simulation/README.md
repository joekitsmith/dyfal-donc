# simulation

A seeded fake learner that runs through the course for weeks of sessions. `poetry run poe simulate` does one run and prints a summary; `--help` lists the options (seed, days, learner profile, forgetting curve, daily limit on new items, and a break from the app).

The fake learner does not use FSRS. If it forgot the way the engine's memory model assumes, the scheduler would be graded against itself. It has its own ground-truth memory instead (`memory.py`, `stability.py`), so the simulator knows the true retention, which no real deployment can observe. An exercise is truly right only if every item in it is recalled.

`pool.py` builds the exercise pool from `curriculum/exercises/`, and `poe simulate` prints its coverage first. One `random.Random(seed)` is passed through the run and nothing reads the clock, so the same seed and settings give an identical `SimulationTrace` (`trace.py`).
