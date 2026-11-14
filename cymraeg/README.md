# cymraeg

Rule-based Welsh language handling: tokenising, mutations and candidate dictionary forms. The core needs nothing beyond the standard library.

- `tokenise(text)`: splits Welsh text into tokens with character offsets. Clitics such as `'n` and `'r` become their own tokens (`i'n` → `i`, `'n`), hyphenated words stay whole and punctuation is dropped.
- `mutate(word, mutation)`: applies a `Mutation` (`SOFT`, `NASAL`, `ASPIRATE`, `H_PROTHESIS`), keeping the initial capital. Words that don't take the mutation come back unchanged.
- `demutate(token)`: every plausible radical form of a possibly mutated token, as `Demutation(radical, mutation)`. The unmutated reading always comes first, then mutations in enum order with radicals sorted. Ambiguity is expected (`las` could be `glas` or `llas`), so callers choose among the candidates.
- `find_demutation(token, radical)`: how `token` reads as the given radical word (ignoring case), or `None`. Prefers the unmutated reading.

## Lemmatisers

A `Lemmatiser` takes the tokens of one sentence and returns the candidate lemmas (dictionary forms) of each token.

- `RuleLemmatiser`: the `demutate` radicals only. It handles mutation, not inflection.
- `SimplemmaLemmatiser`: looks each word up with [Simplemma](https://github.com/adbar/simplemma), which also handles inflection (`gwelais` → `gweld`).
- `StanzaLemmatiser`: [Stanza](https://stanfordnlp.github.io/stanza/)'s Welsh model, using the sentence as context. It is given the `tokenise` tokens as they are. The model (about 200 MB) downloads on first use.
- `DemutatingLemmatiser(inner)`: also lemmatises each token as every radical it could be a mutation of, so a lemmatiser that ignores mutation can be combined with `demutate`.

Simplemma and Stanza are in the optional `lemmatisers` Poetry group, so the default install stays light: `poetry install --with lemmatisers`. Then `poetry run poe download-stanza-model` fetches the Stanza model ahead of time. The adapters import their library only when constructed, and their tests skip when it is missing.

`cymraeg` knows Welsh, not our curriculum, so it must never import `engine`. A unit test enforces this.
