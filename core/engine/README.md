# engine

The pure core of the course: state in, decisions out. No database, network or LLM. The only file access is the curriculum loader.

## `engine.curriculum`

The curriculum is a prerequisite graph of **items**, plus the intended learning order.

- `Lexeme`: a word, e.g. `siarad`, with the other `forms` a learner is taught (`llyfr`: `llyfrau`). Forms are declared, not guessed, so validation stays exact. A form shared by two lexemes must be declared in `homographs` on both.
- `Pattern`: a grammar pattern with typed slots, e.g. `Dw i'n [VERB]`.
- `topic`: a lowercase tag on every `Lexeme` and `Pattern` that groups items for authors. The loader sets it from the name of the file the item is in (`lexemes/food.yaml` gives `food`), and `spine` is read first. It does not affect scheduling.
- `Topic`: a name and the names of the topics it `requires`. A `Curriculum` can carry its topics, in the order they are taught. Construction then checks that each topic follows what it requires, that every item is in a known topic, and that an item only has prerequisites in its own topic or in a topic it requires.
- `Curriculum`: the items and the order. Construction validates unique ids, existing prerequisites, no cycles (the error shows the cycle path) and that the order respects prerequisites. `known_before(item_id)` is what a learner can be assumed to know on meeting the item: the earlier items of its topic plus every item of the topics it requires, however the topics are sequenced.
- `load_curriculum(path)`: reads a [curriculum directory](../../curriculum/README.md): `topics.yaml` and the `lexemes/`, `patterns/` and `order/` directories (one file per topic). The order of the course is each topic's order, one topic after another.
- `topological_order()`: a deterministic ordering derived from the graph alone.

The models are plain frozen dataclasses. Pydantic is used only in the loader, to parse YAML.

## `engine.detection`

Finds curriculum items in Welsh text. Independent of exercises, so it can be reused wherever text needs explaining in curriculum terms.

- `CurriculumIndex.from_curriculum(curriculum)`: prepares a curriculum for lookup: patterns as fixed tokens and slots, multi-word lexemes as phrases, single words keyed by casefolded text, one entry per declared form. `candidates(token_text)` lists the lexemes a token could be, undoing mutations.
- `detect_items(text, index, preferred)`: tokenises the text with [`cymraeg`](../cymraeg/README.md) and tries patterns (one single-token filler per slot), then multi-word lexemes, then single words. Ambiguity resolves to an unmutated reading, then `preferred` items, then `demutate` order.
- `Detection`: the `DetectedItem`s (id, span, form matched, mutation undone) and `problems` in text order: `UnknownToken` and `SlotPartOfSpeechMismatch`.

Known limitations: mutated fixed tokens in a pattern aren't matched, a slot filler is a single token, and a mutation is accepted without checking that its trigger is present.

## `engine.exercises`

Checks an `Exercise` (English, Welsh, declared item ids, optional `new_item`) against the curriculum.

- `validate_exercise(exercise, curriculum, known_items)`: runs detection, then compares the detected items with the declared ones. `known_items` are the ids taught before this exercise, so any detected item outside it is new, and an exercise may introduce at most one.
- `load_exercises(directory)`: reads every `*.yaml` pack in the directory into `ExerciseEntry` objects (`id`, `pack`, `exercise`), and checks the shape of the files, not the Welsh. `exercise_pool(entries)` maps ids to exercises, as the scheduler takes them.
- `ValidationResult`: the detected items and a tuple of typed issues: the detection problems plus `UndeclaredItem`, `DeclaredItemNotFound`, `UnknownDeclaredItem`, `MissingNewItem`, `MultipleNewItems` and `WrongNewItem`. `is_valid` means no issues.

## `engine.authoring`

Helps an author extend the curriculum.

- `suggest_forms(text, index, lemmatiser)`: for each token that detection reports as unknown, asks the [`Lemmatiser`](../cymraeg/README.md) (given the whole sentence) for its lemmas. A lemma that matches a single-word lexeme becomes a `FormSuggestion`: the form to declare, the lexeme and its English gloss, and the lemma behind it. A token is read as written first. Only if that suggests nothing is it read as a mutation of each radical it could be, so a mutated inflected word is suggested by its radical.
- Suggestions are proposals. A lemmatiser can be wrong, so a person should approve each one before it is declared in `forms`.

The lemmatiser is passed in, so the engine never imports Simplemma or Stanza. The command-line tool is `poe suggest-forms`, in [`backend/tools/`](../../backend/tools/suggest_forms.py).

## `engine.learner`

What the learner knows, derived purely from a log of review events. No clock, randomness or I/O: every time-dependent call takes a timezone-aware UTC `now`, and naive or non-UTC datetimes raise `LearnerError`.

- `ReviewEvent`: one exercise given (`exercise_id`, `item_ids`, `new_item`, `outcome`, `reviewed_at`). `Outcome` is `GOT_IT` or `MISSED_IT`. A learner who says nothing is assumed to have got it, so the caller records only reported misses as `MISSED_IT`.
- `replay(events)` and `apply_event(state, event)`: the same fold, so replaying everything equals applying events one at a time. Events must be chronological, may only practise introduced items, and may introduce an item only once.
- `LearnerState`: an item id mapped to its memory. No entry means never introduced.
  - `Learning`: short-term steps counted in **exercises**, not time (default `(1, 3, 8)`: one other exercise, then three, then eight). A miss returns to the first step, and passing the last one graduates the item.
  - `Review`: long-term memory, scheduled by a `MemoryModel`.
- `FsrsMemoryModel`: the `MemoryModel` backed by [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs), with its learning steps and fuzzing off. It is the only module that imports `fsrs`. Intervals are whole days, so even a lapse is due the next day, and they are capped at 180 days so that a well-known item still comes back now and then.
- `assign_credit(state, event, memory_model)`: the weakest link.
  - A success counts only for items that are due, so practising an item early cannot inflate its stability. `LearnerSettings.review_credit_fraction` (default 1.0) lowers that bar: at 0.5 a `Review` item counts once half its interval has passed. It is off by default, so that it can be measured before it is used.
  - A miss goes to the newest material: every `Learning` item if there is one or the exercise introduces an item, and otherwise the single `Review` item least likely to be recalled (lowest id on a tie).
  - Every exercise counts all `Learning` items down by one.
- Queries: `introduced_items`, `learning_items_due`, `review_items_due(state, now)` (longest overdue first) and `recent_error_rate(events, window)`, the share of the last `window` events that were misses.

Known limitations: a lapsed `Review` item is not relearned within the session, only two of FSRS's four ratings are used, and a long break does not expire `Learning` items.

## `engine.scheduler`

Chooses the next exercise. Pure like the rest: the same inputs always give the same answer.

`next_exercise(pool, curriculum, state, recent_events, now, settings)` takes `pool`, a mapping of exercise id to published `Exercise`, and returns a `Selection` or a `NothingEligible`.

- The **frontier** is the first curriculum item (in order) the learner has not met.
- An exercise is **eligible** if the learner has met every item in it, or if the only item they have not met is the frontier item and the exercise introduces it (`new_item`).
- Priority: an exercise practising a `Learning` item that is due, then a `Review` item that is due, then the exercise introducing the frontier item (only while the recent error rate is under 15%), then any eligible exercise as extra practice. Introducing exercises never count as due practice, so the error-rate limit cannot be bypassed.
- Within a priority the best score wins: each due item, each item shared with the previous exercise (so phrases build up), and no immediate repeat. The lowest exercise id breaks a tie.
- Until there are five recent events the error rate is ignored, so one early miss cannot stall the course.
- `SchedulerSettings.new_items_per_day` (off by default) caps how many items are introduced on one UTC calendar day, counted from the events passed in, so they must include everything from today.
- `Selection` says why it was chosen (`Purpose`) and what it `introduces`, and `as_event(outcome, reviewed_at)` builds the `ReviewEvent`. Use that, not `exercise.new_item`, since an exercise that once introduced an item is ordinary practice afterwards.
- `NothingEligible` has a reason. `NO_EXERCISE_INTRODUCES_FRONTIER` means the pool has no exercise for the next item, a gap for authors to fill. `ERROR_RATE_TOO_HIGH` means introductions are held back and there is nothing to practise, and `NEW_ITEM_LIMIT_REACHED` means the same for the daily limit.

Known limitations: no cap on how many items are in `Learning` at once, and exercise choice does not yet use difficulty or variety beyond the previous exercise.
