from dataclasses import fields
from pathlib import Path

import yaml
from pydantic import TypeAdapter, ValidationError

from engine.curriculum.errors import CurriculumError
from engine.curriculum.models import (
    DEFAULT_TOPIC,
    Curriculum,
    Item,
    Lexeme,
    Pattern,
    Topic,
)

PATTERNS_DIRECTORY = "patterns"
LEXEMES_DIRECTORY = "lexemes"
ORDER_DIRECTORY = "order"
TOPICS_FILE = "topics.yaml"


def load_curriculum(path: str | Path) -> Curriculum:
    """Load and validate a curriculum directory.

    ``topics.yaml`` lists the topics in the order they are taught, each with
    the topics it requires. The ``patterns``, ``lexemes`` and ``order``
    directories each hold one ``<topic>.yaml`` file per topic: the items of that
    topic, and the order they are taught in within it. The topic of an item is
    the name of the file it is in. The order of the whole course is each topic's
    order, one topic after another, in the sequence of ``topics.yaml``.
    """
    root = Path(path)
    topics = _load_topics(root / TOPICS_FILE)
    items: tuple[Item, ...] = (
        *_load_directory(root / PATTERNS_DIRECTORY, Pattern),
        *_load_directory(root / LEXEMES_DIRECTORY, Lexeme),
    )
    order = _load_order(root / ORDER_DIRECTORY, topics, items)

    return Curriculum(items=items, order=order, topics=topics)


def _read_list(path: Path) -> tuple[object, ...]:
    if not path.is_file():
        raise CurriculumError(f"Missing file: {path}")

    try:
        data: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CurriculumError(f"{path}: Invalid YAML: {exc}") from exc

    if not isinstance(data, list):
        raise CurriculumError(f"{path}: Expected a YAML list at top level")

    return tuple(data)


def _load_topics(path: Path) -> tuple[Topic, ...]:
    topics: list[Topic] = []
    for index, raw in enumerate(_read_list(path)):
        if not isinstance(raw, dict):
            raise CurriculumError(f"{path}[{index}]: Expected a mapping")

        label = f"{path} ({raw.get('name', f'#{index}')})"
        unknown = sorted(str(key) for key in raw if key not in {"name", "requires"})
        if unknown:
            raise CurriculumError(f"{label}: Unknown field(s): {', '.join(unknown)}")

        name, requires = raw.get("name"), raw.get("requires", [])
        if not isinstance(name, str):
            raise CurriculumError(f"{label}: A topic needs a name")

        if not isinstance(requires, list) or not all(
            isinstance(required, str) for required in requires
        ):
            raise CurriculumError(f"{label}: Requires must be a list of topic names")

        try:
            topics.append(Topic(name=name, requires=tuple(requires)))
        except CurriculumError as exc:
            raise CurriculumError(f"{path}: {exc}") from exc

    return tuple(topics)


def _load_order(
    directory: Path, topics: tuple[Topic, ...], items: tuple[Item, ...]
) -> tuple[str, ...]:
    if not directory.is_dir():
        raise CurriculumError(f"Missing directory: {directory}")

    names = {topic.name for topic in topics}
    for file in sorted(directory.glob("*.yaml")):
        if file.stem not in names:
            raise CurriculumError(f"{file}: Unknown topic {file.stem}")

    topic_of = {item.id: item.topic for item in items}
    order: list[str] = []
    for topic in topics:
        file = directory / f"{topic.name}.yaml"
        for entry in _read_list(file):
            if not isinstance(entry, str):
                raise CurriculumError(f"{file}: Every entry must be an item id string")

            if topic_of.get(entry, topic.name) != topic.name:
                raise CurriculumError(
                    f"{file}: {entry} belongs to topic {topic_of[entry]}, not {topic.name}"
                )

            order.append(entry)

    return tuple(order)


def _load_directory[T: (Lexeme, Pattern)](
    directory: Path, model: type[T]
) -> tuple[T, ...]:
    if not directory.is_dir():
        raise CurriculumError(f"Missing directory: {directory}")

    files = sorted(
        directory.glob("*.yaml"),
        key=lambda file: (file.stem != DEFAULT_TOPIC, file.stem),
    )
    return tuple(
        item for file in files for item in _load_items(file, model, topic=file.stem)
    )


def _load_items[T: (Lexeme, Pattern)](
    path: Path, model: type[T], *, topic: str
) -> tuple[T, ...]:
    adapter = TypeAdapter(model)
    known_fields = {field.name for field in fields(model)}

    items: list[T] = []
    for index, raw in enumerate(_read_list(path)):
        if not isinstance(raw, dict):
            raise CurriculumError(f"{path}[{index}]: Expected a mapping")

        label = raw.get("id", f"#{index}")
        if "topic" in raw:
            raise CurriculumError(
                f"{path} ({label}): The topic comes from the file name, so remove 'topic'"
            )

        unknown = sorted(str(key) for key in raw if key not in known_fields)
        if unknown:
            raise CurriculumError(
                f"{path} ({label}): Unknown field(s): {', '.join(unknown)}"
            )

        try:
            items.append(adapter.validate_python({**raw, "topic": topic}))
        except CurriculumError as exc:
            raise CurriculumError(f"{path} ({label}): {exc}") from exc
        except ValidationError as exc:
            details = "; ".join(
                f"{'.'.join(map(str, error['loc'])) or 'item'}: {error['msg']}"
                for error in exc.errors()
            )
            raise CurriculumError(f"{path} ({label}): {details}") from exc

    return tuple(items)
