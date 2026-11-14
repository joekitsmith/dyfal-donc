# cymraeg

Rule-based Welsh language handling: tokenising, mutations and candidate dictionary forms. No dependencies beyond the standard library.

- `tokenise(text)`: splits Welsh text into tokens with character offsets. Clitics such as `'n` and `'r` become their own tokens (`i'n` → `i`, `'n`), hyphenated words stay whole and punctuation is dropped.
- `mutate(word, mutation)`: applies a `Mutation` (`SOFT`, `NASAL`, `ASPIRATE`, `H_PROTHESIS`), keeping the initial capital. Words that don't take the mutation come back unchanged.
- `demutate(token)`: every plausible radical form of a possibly mutated token, as `Demutation(radical, mutation)`. The unmutated reading always comes first, then mutations in enum order with radicals sorted. Ambiguity is expected (`las` could be `glas` or `llas`), so callers choose among the candidates.

`cymraeg` knows Welsh, not our curriculum, so it must never import `engine`. A unit test enforces this.
