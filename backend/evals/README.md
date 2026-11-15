# evals

Measurements of quality, kept apart from the tests. The tests check behaviour, while the evals score how well the tools do.

## `evals.gold`

`gold/sentences/` holds South Wales sentences, annotated per token, one file per topic. `hand.yaml` is the original hand-written set. The other files are the sentences of the course's own exercises, one per exercise in the matching pack. `load_gold_sentences()` parses and validates them, and the integration tests check them against the curriculum and `tokenise()`.

Each token is annotated with:

- `lemma`: the dictionary form (`Dw` is `bod`, `'n` is `yn`). Lemmas follow the conventions of the [Welsh UD treebank](https://universaldependencies.org/treebanks/cy_ccg) (CC BY-SA 4.0).
- `item`: the lexeme id the token should be detected as, or nothing if it is not a lexeme. Expected items follow the lemma, so an inflected form the curriculum doesn't declare yet (`gwelais`) still expects `lex:gweld`.
- `mutation`: the mutation on the token.

Each sentence also lists the `patterns` it is an instance of, and `tags` for what it tests.

## `evals.benchmark`

`poetry run poe benchmark` scores lemmatisers on the gold sentences and writes [`reports/lemmatiser-benchmark.md`](reports/lemmatiser-benchmark.md). It needs the optional `lemmatisers` group (`poetry install --with lemmatisers`). `lemma_level.py`, `item_level.py` and `authoring.py` hold the scoring, and the functions are pure, so they are tested with fake lemmatisers. The report's recommendation is written by hand in `benchmark/recommendation.md` and included as it is, so regenerating the report doesn't change it.
