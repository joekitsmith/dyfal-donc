# curriculum

Hand-authored seed data, in South Wales Welsh (`Dw i'n moyn`, not `Dw i eisiau`). Loaded by `engine.curriculum.load_curriculum`.

- `lexemes/<topic>.yaml`: words, with `part_of_speech`, optional `gender` (nouns only), `forms` (other forms a learner is taught: plurals, inflections, variants, clitics such as `'r`) and `notes`. Every form must be unique across the curriculum, unless the lexemes sharing it list each other in `homographs`.
- `patterns/<topic>.yaml`: templates with `[SLOT]`s. Each slot is declared in `slots` with the part of speech that may fill it, e.g. `slots: {VERB: verb}`.
- `topics.yaml`: the topics in the order they are taught, each with the topics it `requires` (`time` requires `spine` and `places`, for instance). A topic comes after everything it requires.
- `order/<topic>.yaml`: the ids of that topic's items, each exactly once, in the order they are taught within the topic.
- `exercises/<pack>.yaml`: the course's exercises, one file per pack, loaded by `engine.exercises.load_exercises`. Each has `id` (unique across all packs), `english`, `welsh`, `items` and an optional `new_item` (the one item it introduces). Every word in `welsh` must be a curriculum item, so an exercise can only be written once its words are declared.

The topic of an item is the name of the file it is in (`lexemes/food.yaml` holds the `food` lexemes, and `spine` is the conversational core), so a file cannot also say `topic:`. The order of the whole course is derived: each topic's order, one topic after another, in the sequence of `topics.yaml`. Reviews of earlier topics come back in between new items, because the scheduler puts what is due before something new. Items may only have prerequisites in their own topic or in a topic they require, and an exercise may only use items of its own topic that come earlier, plus every item of the topics it requires. So the sequence of topics can change without breaking an exercise.

The course is the `spine` (pronouns, common verbs, the present, past and future, questions) followed by eight topic packs, taught in this order: `food`, `hobbies`, `weather`, `family`, `home`, `work`, `places`, `time`. Each pack has its own file in `exercises/` as well as in `lexemes/` and `patterns/`, and its own gold sentences in `backend/evals/gold/sentences/`. Every item has at least three exercises that introduce it, except a few of the very first (`siarad`, `cymraeg`, `dw-in-moyn`, `mynd`, `dod`), for which nothing more can be built from what is known by then.

Items can list `prerequisites` (ids of other items). An item must come after all of its prerequisites in the derived order.

Check your edits with `poetry run poe tests-integration`, which validates every exercise against the curriculum and checks that slot words show the mutation their pattern requires (`Galla i fynd`, not `Galla i mynd`), since validation alone accepts either. Errors name the file and item at fault.

## Finding forms to declare

`poetry run poe suggest-forms "Gwelais i e neithiwr"` (after `poetry install --with lemmatisers`) lists unknown words that look like a form of a curriculum word, with the `forms:` line to paste. It uses Stanza by default, because it was the more accurate in the [benchmark](../backend/evals/reports/lemmatiser-benchmark.md); the first run downloads its 200 MB Welsh model. It also takes `--file` (one sentence per line) and `--lemmatiser simplemma`, which is lighter and faster but makes more wrong suggestions. The suggestions can be wrong, so check each one. A suggested form for a mutated word may be the mutated spelling rather than the radical: declare the radical (`gwela`, not `wela`).
