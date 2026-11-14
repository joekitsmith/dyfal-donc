# engine

The pure core of the course: state in, decisions out. No database, network or LLM. The only file access is the curriculum loader.

## `engine.curriculum`

The curriculum is a prerequisite graph of **items**, plus the intended learning order.

- `Lexeme`: a word, e.g. `siarad`.
- `Pattern`: a grammar pattern with typed slots, e.g. `Dw i'n [VERB]`.
- `Curriculum`: the items and the order. Construction validates unique ids, existing prerequisites, no cycles (the error shows the cycle path) and that the order respects prerequisites.
- `load_curriculum(path)`: reads a [curriculum directory](../curriculum/README.md).
- `topological_order()`: a deterministic ordering derived from the graph alone.

The models are plain frozen dataclasses. Pydantic is used only in the loader, to parse YAML.
