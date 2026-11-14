# cymraeg

Rule-based Welsh language handling: tokenising, mutations and candidate dictionary forms. No dependencies beyond the standard library.

- `tokenise(text)`: splits Welsh text into tokens with character offsets. Clitics such as `'n` and `'r` become their own tokens (`i'n` → `i`, `'n`), hyphenated words stay whole and punctuation is dropped.

`cymraeg` knows Welsh, not our curriculum, so it must never import `engine`. A unit test enforces this.
