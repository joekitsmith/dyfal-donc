from collections.abc import Set as AbstractSet
from dataclasses import fields
from pathlib import Path

import yaml
from pydantic import TypeAdapter, ValidationError

from evals.gold.errors import GoldSetError
from evals.gold.models import GoldSentence

SENTENCES_DIRECTORY = Path(__file__).parent / "sentences"


def load_gold_sentences(
    path: str | Path = SENTENCES_DIRECTORY,
) -> tuple[GoldSentence, ...]:
    """Load and validate the gold sentences.

    ``path`` is a directory of ``*.yaml`` files, read in file name order, or a
    single file. Ids must be unique across all the files.
    """
    root = Path(path)
    files = tuple(sorted(root.glob("*.yaml"))) if root.is_dir() else (root,)
    adapter = TypeAdapter(GoldSentence)
    known_fields = {field.name for field in fields(GoldSentence)}

    sentences = tuple(
        _parse_sentence(adapter, known_fields, raw, index, file)
        for file in files
        for index, raw in enumerate(_read_list(file))
    )

    _check_unique_ids(sentences, root)

    return sentences


def _read_list(path: Path) -> tuple[object, ...]:
    if not path.is_file():
        raise GoldSetError(f"Missing file: {path}")

    try:
        data: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise GoldSetError(f"{path}: Invalid YAML: {exc}") from exc

    if not isinstance(data, list):
        raise GoldSetError(f"{path}: Expected a YAML list at top level")

    return tuple(data)


def _parse_sentence(
    adapter: TypeAdapter[GoldSentence],
    known_fields: AbstractSet[str],
    raw: object,
    index: int,
    path: Path,
) -> GoldSentence:
    if not isinstance(raw, dict):
        raise GoldSetError(f"{path}[{index}]: Expected a mapping")

    label = raw.get("id", f"#{index}")
    unknown = sorted(str(key) for key in raw if key not in known_fields)
    if unknown:
        raise GoldSetError(f"{path} ({label}): Unknown field(s): {', '.join(unknown)}")

    try:
        return adapter.validate_python(raw)
    except GoldSetError as exc:
        raise GoldSetError(f"{path} ({label}): {exc}") from exc
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(map(str, error['loc'])) or 'sentence'}: {error['msg']}"
            for error in exc.errors()
        )
        raise GoldSetError(f"{path} ({label}): {details}") from exc


def _check_unique_ids(sentences: tuple[GoldSentence, ...], path: Path) -> None:
    ids = [sentence.id for sentence in sentences]
    duplicates = sorted(
        {sentence_id for sentence_id in ids if ids.count(sentence_id) > 1}
    )
    if duplicates:
        raise GoldSetError(f"{path}: Duplicate sentence ids: {', '.join(duplicates)}")
