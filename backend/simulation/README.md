# simulation

A seeded fake learner that runs through the course for weeks of sessions, so engine settings can be tuned on evidence. `poetry run poe simulate` does one run and prints a summary (`--seed`, `--days`, `--profile strong|average|weak`, `--memory exponential|power-law`).

## The simulated learner does not use FSRS

If the fake learner forgot the way the engine's memory model assumes, the scheduler would be graded against itself. The learner has its own ground-truth memory instead (`memory.py`), so the simulator knows the **true retention**, which no real deployment can observe.

- **Two forgetting curves.** `ExponentialMemory` has a constant rate of forgetting and `PowerLawMemory` forgets fast then slowly (closest to FSRS). Both define stability as the time for recall to fall to 90%, so they are comparable. Trust a conclusion only if it holds under both.
- **Updates are one explicit rule** (`StabilityUpdate`): a success multiplies stability, more so when recall was hard (the spacing effect), and a failure keeps 30% of it. New items start at 0.01 days (about 15 minutes), so in-session learning steps matter.
- **An exercise is truly right only if every item is recalled.** Each item's memory updates on its own result, whatever the engine's weakest-link credit assignment does.
- **Reporting.** A true miss is reported as `MISSED_IT` unless the learner stays silent (`under_report_rate`). A hit is always reported as a success.
- **Per-item difficulty** is a log-normal multiplier on how much a success helps, derived from the seed and the item id, so it does not depend on the order items are introduced in.

The gains and failure penalty are assumptions, set so an average learner looks plausible, not fitted to real data. Read results as differences between settings, not absolute retention.

## The exercise pool

`pool.py` builds exercises from the hand-annotated gold sentences that validate against the curriculum (each introduces the latest item in the course order that it uses), plus `exercises.yaml`. Only 43 of the 181 gold sentences validate, because they were written to test tokenising and lemmatising and mostly use words outside the curriculum. The 24 extra exercises fill the gaps so that every item can be introduced. They are generated and not yet reviewed by a fluent speaker. `poe simulate` prints the pool's coverage first.

## Determinism

One `random.Random(seed)` is passed through the run, and nothing reads the clock or global randomness. The same seed and settings give an identical `SimulationTrace`.
