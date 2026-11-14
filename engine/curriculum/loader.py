from dataclasses import fields
from pathlib import Path

import yaml
from pydantic import TypeAdapter, ValidationError

from engine.curriculum.errors import CurriculumError
from engine.curriculum.models import Curriculum, Item, Lexeme, Pattern

PATTERNS_FILE = "patterns.yaml"
LEXEMES_FILE = "lexemes.yaml"
ORDER_FILE = "order.yaml"


def load_curriculum(path: str | Path) -> Curriculum:
    """Load and validate ``patterns.yaml``, ``lexemes.yaml`` and ``order.yaml``."""
    root = Path(path)
    items: tuple[Item, ...] = (
        *_load_items(root / PATTERNS_FILE, Pattern),
        *_load_items(root / LEXEMES_FILE, Lexeme),
    )
    order_path = root / ORDER_FILE
    order = _read_list(order_path)
    if not all(isinstance(entry, str) for entry in order):
        raise CurriculumError(f"{order_path}: every entry must be an item id string")
    return Curriculum(items=items, order=tuple(str(entry) for entry in order))


def _read_list(path: Path) -> tuple[object, ...]:
    if not path.is_file():
        raise CurriculumError(f"missing file: {path}")
    try:
        data: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CurriculumError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(data, list):
        raise CurriculumError(f"{path}: expected a YAML list at top level")
    return tuple(data)


def _load_items[T: (Lexeme, Pattern)](path: Path, model: type[T]) -> tuple[T, ...]:
    adapter = TypeAdapter(model)
    known_fields = {field.name for field in fields(model)}
    items: list[T] = []
    for index, raw in enumerate(_read_list(path)):
        if not isinstance(raw, dict):
            raise CurriculumError(f"{path}[{index}]: expected a mapping")
        unknown = sorted(str(key) for key in raw if key not in known_fields)
        if unknown:
            raise CurriculumError(
                f"{path} ({raw.get('id', f'#{index}')}): "
                f"unknown field(s): {', '.join(unknown)}"
            )
        try:
            items.append(adapter.validate_python(raw))
        except CurriculumError as exc:
            raise CurriculumError(
                f"{path} ({raw.get('id', f'#{index}')}): {exc}"
            ) from exc
        except ValidationError as exc:
            label = raw.get("id", f"#{index}")
            details = "; ".join(
                f"{'.'.join(map(str, error['loc'])) or 'item'}: {error['msg']}"
                for error in exc.errors()
            )
            raise CurriculumError(f"{path} ({label}): {details}") from exc
    return tuple(items)
