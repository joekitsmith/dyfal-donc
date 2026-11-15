# curriculum

The course content, in South Wales Welsh (`Dw i'n moyn`, not `Dw i eisiau`). Loaded by `engine.curriculum.load_curriculum`.

- `topics.yaml`: the topics in the order they are taught, each with the topics it `requires`. `spine` is the conversational core.
- `lexemes/<topic>.yaml`: words, with `part_of_speech`, optional `gender` (nouns only), `forms` (other forms a learner is taught: plurals, inflections, variants, clitics such as `'r`) and `notes`. Every form must be unique across the curriculum, unless the lexemes sharing it list each other in `homographs`.
- `patterns/<topic>.yaml`: templates with `[SLOT]`s. Each slot is declared in `slots` with the part of speech that may fill it, e.g. `slots: {VERB: verb}`.
- `order/<topic>.yaml`: the ids of that topic's items, each exactly once, in the order they are taught.
- `exercises/<pack>.yaml`: exercises, one file per pack, loaded by `engine.exercises.load_exercises`. Each has `id` (unique across all packs), `english`, `welsh`, `items` and an optional `new_item` (the one item it introduces). Every word in `welsh` must be a curriculum item, so an exercise can only be written once its words are declared.

The topic of an item is the name of the file it is in, so a file cannot also say `topic:`. The order of the whole course is derived from the topic order and each topic's own order. Items can list `prerequisites`, which must be in the item's own topic or a topic it requires, and must come first. An exercise may use earlier items of its own topic plus every item of the topics it requires.

Check your edits with `poetry run poe tests-integration`. It validates every exercise against the curriculum and checks that slot words show the mutation their pattern requires (`Galla i fynd`, not `Galla i mynd`), which validation alone accepts either way. Errors name the file and item at fault.

## Finding forms to declare

`poetry run poe suggest-forms "Gwelais i e neithiwr"` (after `poetry install --with lemmatisers`) lists unknown words that look like a form of a curriculum word, with the `forms:` line to paste. `--help` lists the options. The suggestions can be wrong, so check each one. A suggested form for a mutated word may be the mutated spelling rather than the radical: declare the radical (`gwela`, not `wela`).
