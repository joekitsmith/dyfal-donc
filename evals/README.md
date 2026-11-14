# evals

Measurements of quality, kept apart from the tests. The tests check behaviour, while the evals score how well the tools do.

## `evals.gold`

`gold/sentences.yaml` holds hand-written South Wales sentences, annotated per token:

- `lemma`: the dictionary form (`Dw` is `bod`, `'n` is `yn`).
- `item`: the lexeme id the token should be detected as, or nothing. Nothing means the token is not a lexeme: it is outside the curriculum, or it is a fixed word of a pattern.
- `mutation`: the mutation on the token (`soft`, `nasal`, `aspirate`, `h_prothesis`).

Each sentence also lists the `patterns` it is an instance of, and `tags` for what it tests: `mutation`, `inflection`, `clitic`, `article` or `plain`. A multi-word lexeme (`fan hyn`) puts its id on each of its tokens. Expected items follow the lemma, so an inflected form the curriculum doesn't declare yet (`gwelais`) still expects `lex:gweld`.

`load_gold_sentences()` parses and validates the file, and the integration tests check it against the curriculum and `tokenise()`.
