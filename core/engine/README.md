# engine

The course logic: state in, decisions out. It has no database, network or LLM, and the only file access is the curriculum loader. Models are plain frozen dataclasses, and each package exports its public names from its `__init__.py`. The docstrings of the entry points below say what they do.

| Package | What it is | Start at |
|---|---|---|
| `curriculum/` | The items (words and grammar patterns), their prerequisites, their topics and the teaching order. See the [curriculum directory](../../curriculum/README.md) for the files it loads. | `models.py`, `loader.py` |
| `detection/` | Finds curriculum items in Welsh text. | `detect.py`, `index.py` |
| `exercises/` | Checks an exercise's Welsh against the curriculum, and loads exercise packs. | `validation.py`, `loader.py` |
| `authoring/` | Suggests forms to declare for words detection doesn't know. A lemmatiser is passed in, so the engine never imports one. | `suggest.py` |
| `learner/` | What the learner knows, derived by replaying review events. | `replay.py`, `credit.py` |
| `scheduler/` | Chooses the next exercise. | `selection.py` |

## How the learn loop fits together

1. `scheduler.next_exercise` takes the exercise pool, the curriculum, the learner's state and recent events, and returns a `Selection` (or `NothingEligible` with a reason).
2. When the learner reports how it went, `Selection.as_event` builds the `ReviewEvent`. Use it instead of reading `exercise.new_item`, because an exercise that once introduced an item is ordinary practice afterwards.
3. `learner.replay` folds the events into a `LearnerState`. State is never stored, only derived, and every time-dependent call takes a UTC `now`.

An item is either `Learning` (short-term steps counted in exercises, not time) or `Review` (scheduled by a `MemoryModel`, with FSRS behind `fsrs_model.py`, the only module that imports it). A miss is credited to the newest material, not to everything in the exercise: see `credit.py`.
