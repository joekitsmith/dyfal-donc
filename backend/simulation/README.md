# simulation

A seeded fake learner that runs through the course for weeks of sessions, so engine settings can be tuned on evidence. `poetry run poe simulate` does one run and prints a summary (`--seed`, `--days`, `--profile strong|average|weak`, `--memory exponential|power-law`, `--new-items-per-day`). Add `--break-start` and `--break-days` to put the app down for a while and see what it costs: the backlog on return, how much of the course is practised again, and true retention before and after.

## The simulated learner does not use FSRS

If the fake learner forgot the way the engine's memory model assumes, the scheduler would be graded against itself. The learner has its own ground-truth memory instead (`memory.py`), so the simulator knows the **true retention**, which no real deployment can observe.

- **Two forgetting curves.** `ExponentialMemory` has a constant rate of forgetting and `PowerLawMemory` forgets fast then slowly (closest to FSRS). Both define stability as the time for recall to fall to 90%, so they are comparable. Trust a conclusion only if it holds under both.
- **Updates are one explicit rule** (`StabilityUpdate`). A success multiplies stability by `1 + gain`, where the gain is zero when the item was fully remembered and grows as more was forgotten (so a hard recall gains more than an easy one, and repeating an item within a minute adds almost nothing). The gain shrinks as the memory strengthens and is capped, which keeps stability from running away. A failure keeps 30% of the stability but never drops below the starting value, since seeing the answer again is a fresh exposure. A new item starts at 0.15 days, scaled by the learner's `learning_rate` and the item's difficulty.
- **An exercise is truly right only if every item is recalled.** Each item's memory updates on its own result, whatever the engine's weakest-link credit assignment does.
- **Reporting.** A true miss is reported as `MISSED_IT` unless the learner stays silent (`under_report_rate`). A hit is always reported as a success.
- **Per-item difficulty** is a log-normal multiplier on how much a success helps, derived from the seed and the item id, so it does not depend on the order items are introduced in.

The gains and failure penalty are assumptions, set so an average learner looks plausible, not fitted to real data. Read results as differences between settings, not absolute retention.

## The exercise pool

`pool.py` loads the course's own exercises from `curriculum/exercises/` and checks that each validates against the curriculum. `poe simulate` prints the pool's coverage first: how many exercises can introduce each item, and the first item (if any) no exercise can introduce, which would stop a learner there.

## Determinism

One `random.Random(seed)` is passed through the run, and nothing reads the clock or global randomness. The same seed and settings give an identical `SimulationTrace`.
