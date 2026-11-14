# dyfal-donc

A spaced-repetition Welsh speaking course (South Wales Welsh) with LLM-assisted, human-curated content. Lessons work in the style of Say Something In: hear the English, say it in Welsh, then hear the Welsh.

**Work in progress.**

## Layout

- [`engine/`](engine/README.md): pure Python core (no I/O beyond loading the curriculum)
- [`cymraeg/`](cymraeg/README.md): rule-based Welsh handling (tokenising, mutations), independent of the engine
- [`curriculum/`](curriculum/README.md): hand-authored YAML seed data
- `tests/`: unit and integration tests, mirroring the code tree

## Development

Requires Python 3.14 and Poetry.

```sh
poetry install
poetry run poe format      # ruff format
poetry run poe lint        # ruff check (lint-fix to apply fixes)
poetry run poe mypy
poetry run poe tests-unit
poetry run poe tests-integration
```
