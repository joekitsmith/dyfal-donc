# engine

The pure core of the course: state in, decisions out. No database, network or LLM. The only file access is the curriculum loader.

## `engine.curriculum`

The curriculum is a prerequisite graph of **items**, plus the intended learning order.

- `Lexeme`: a word, e.g. `siarad`, with the other `forms` a learner is taught (`llyfr`: `llyfrau`). Forms are declared, not guessed, so validation stays exact. A form shared by two lexemes must be declared in `homographs` on both.
- `Pattern`: a grammar pattern with typed slots, e.g. `Dw i'n [VERB]`.
- `Curriculum`: the items and the order. Construction validates unique ids, existing prerequisites, no cycles (the error shows the cycle path) and that the order respects prerequisites.
- `load_curriculum(path)`: reads a [curriculum directory](../../curriculum/README.md).
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
- `FsrsMemoryModel`: the `MemoryModel` backed by [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs), with its learning steps and fuzzing off. It is the only module that imports `fsrs`. Intervals are whole days, so even a lapse is due the next day.
- `assign_credit(state, event, memory_model)`: the weakest link.
  - A success counts only for items that are due, so practising an item early cannot inflate its stability.
  - A miss goes to the newest material: every `Learning` item if there is one or the exercise introduces an item, and otherwise the single `Review` item least likely to be recalled (lowest id on a tie).
  - Every exercise counts all `Learning` items down by one.
- Queries: `introduced_items`, `learning_items_due`, `review_items_due(state, now)` (longest overdue first) and `recent_error_rate(events, window)`, the share of the last `window` events that were misses.

Known limitations: a lapsed `Review` item is not relearned within the session, only two of FSRS's four ratings are used, and a long break does not expire `Learning` items.
