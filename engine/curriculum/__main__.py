import sys
from collections.abc import Sequence

from engine.curriculum.errors import CurriculumError
from engine.curriculum.loader import load_curriculum
from engine.curriculum.models import Lexeme


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python -m engine.curriculum <curriculum-dir>", file=sys.stderr)
        return 2
    try:
        curriculum = load_curriculum(args[0])
    except CurriculumError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for position, item_id in enumerate(curriculum.order, start=1):
        item = curriculum.get(item_id)
        text = item.welsh if isinstance(item, Lexeme) else item.template
        print(f"{position:3}. {item_id:<24} {text}")
    print(f"\nOK: {len(curriculum.order)} items, order respects prerequisites.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
