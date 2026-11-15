# cymraeg

Rule-based Welsh language handling that needs nothing beyond the standard library. Mutation is regular, so it is done by rule here. Inflection is not, so the curriculum declares each form.

| Module | What it is |
|---|---|
| `tokenise.py` | Splits text into tokens with offsets. Clitics such as `'n` are their own tokens. |
| `mutation.py` | `mutate` applies a mutation, and `demutate` and `find_demutation` undo one. A mutated token is ambiguous (`las` could be `glas` or `llas`), so `demutate` returns every candidate and the caller chooses. |
| `lemmatise.py` | The `Lemmatiser` protocol: the tokens of a sentence in, candidate dictionary forms out. |
| `lemmatisers/` | The implementations: rule-based, [Simplemma](https://github.com/adbar/simplemma) and [Stanza](https://stanfordnlp.github.io/stanza/). |

Simplemma and Stanza are in the optional `lemmatisers` Poetry group (`poetry install --with lemmatisers`), and their adapters import the library only when constructed. `poetry run poe download-stanza-model` fetches the Stanza model ahead of time.

`cymraeg` knows Welsh, not our curriculum, so it must never import `engine`. A unit test enforces this.
