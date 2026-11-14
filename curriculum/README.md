# curriculum

Hand-authored seed data, in South Wales Welsh (`Dw i'n moyn`, not `Dw i eisiau`). Loaded by `engine.curriculum.load_curriculum`.

- `lexemes.yaml`: words, with `part_of_speech`, optional `gender` (nouns only), `forms` (other forms a learner is taught: plurals, inflections, variants, clitics such as `'r`) and `notes`. Every form must be unique across the curriculum, unless the lexemes sharing it list each other in `homographs`.
- `patterns.yaml`: templates with `[SLOT]`s. Each slot is declared in `slots` with the part of speech that may fill it, e.g. `slots: {VERB: verb}`.
- `order.yaml`: every item id exactly once, in teaching order.

Items can list `prerequisites` (ids of other items). An item must come after all of its prerequisites in `order.yaml`.

Check your edits with `poetry run poe tests-integration`. Errors name the file and item at fault.

## Finding forms to declare

`poetry run poe suggest-forms "Gwelais i e neithiwr"` (after `poetry install --with lemmatisers`) lists unknown words that look like a form of a curriculum word, with the `forms:` line to paste. It also takes `--file` (one sentence per line) and `--lemmatiser stanza`. The suggestions can be wrong, so check each one. A suggested form for a mutated word may be the mutated spelling rather than the radical: declare the radical (`gwela`, not `wela`).
