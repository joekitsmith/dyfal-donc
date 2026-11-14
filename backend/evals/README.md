# evals

Measurements of quality, kept apart from the tests. The tests check behaviour, while the evals score how well the tools do.

## `evals.gold`

`gold/sentences.yaml` holds hand-written South Wales sentences, annotated per token:

- `lemma`: the dictionary form (`Dw` is `bod`, `'n` is `yn`).
- `item`: the lexeme id the token should be detected as, or nothing. Nothing means the token is not a lexeme: it is outside the curriculum, or it is a fixed word of a pattern.
- `mutation`: the mutation on the token (`soft`, `nasal`, `aspirate`, `h_prothesis`).

Lemmas follow the conventions of the [Welsh UD treebank](https://universaldependencies.org/treebanks/cy_ccg) (CC BY-SA 4.0), so scores aren't an artefact of one annotator's choices: `Dw`, `Mae` and `Wyt` are `bod`, `'n`, `yng` and `ym` are `yn`, `ddim` is `dim`, `ddoe` is `doe`, `heddi` is `heddiw`, `fory` is `yfory`, `moyn` is `ymofyn`, possessive `ei` is `ef` or `hi` by who it refers to, and `fy`, `fi` and `mi` are `i`. The fixed phrase `fan hyn` is annotated as the curriculum's one phrase (`fan` is not marked as soft-mutated `man`). The treebank is also where the real-world failure cases for the new sentences came from. Its written, standard forms mean most colloquial South Wales forms (`-es i`, `-on ni`, `galla i`) do not occur in it, so those were not checked against it.

Each sentence also lists the `patterns` it is an instance of, and `tags` for what it tests: `mutation`, `inflection`, `clitic`, `article` or `plain`. A multi-word lexeme (`fan hyn`) puts its id on each of its tokens. Expected items follow the lemma, so an inflected form the curriculum doesn't declare yet (`gwelais`) still expects `lex:gweld`.

`load_gold_sentences()` parses and validates the file, and the integration tests check it against the curriculum and `tokenise()`.

## `evals.benchmark`

`poetry run poe benchmark` scores lemmatisers on the gold sentences and writes [`reports/lemmatiser-benchmark.md`](reports/lemmatiser-benchmark.md). It needs the optional `lemmatisers` group (`poetry install --with lemmatisers`), and downloads the Stanza model on first run.

- **Lemma level:** how often the gold lemma is among a lemmatiser's candidates, and how many candidates it gives, overall and by tag.
- **Item level:** precision and recall of `detect_items`, with each lemmatiser's lemmas also matching lexemes, against declared forms only.
- **Authoring aid:** how many undeclared forms of curriculum words each lemmatiser maps to the right lexeme, and how many wrong suggestions it makes.
- **Runtime:** milliseconds per sentence.

The scoring functions are pure and take candidates as data, so they are tested with fake lemmatisers. The report's recommendation is written by hand in `benchmark/recommendation.md` and included as it is, so regenerating the report doesn't change it. Rewrite it when the numbers change.
