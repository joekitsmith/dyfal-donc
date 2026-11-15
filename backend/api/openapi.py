import json
import sys
from collections.abc import Sequence
from pathlib import Path

from api.app import create_app
from api.settings import Settings
from persistence.database import DatabaseSettings

UNUSED_DATABASE_URL = "postgresql+psycopg://unused/unused"  # pragma: allowlist secret


def render_openapi_schema() -> str:
    """The API's OpenAPI schema as stable JSON, built without starting the app."""

    settings = Settings(database=DatabaseSettings(url=UNUSED_DATABASE_URL))
    schema = create_app(settings).openapi()
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def main(arguments: Sequence[str] | None = None) -> int:
    """Write the schema to the one path given, for the frontend's generated types."""

    paths = sys.argv[1:] if arguments is None else arguments
    if len(paths) != 1:
        print("Usage: python -m api.openapi PATH", file=sys.stderr)
        return 2
    Path(paths[0]).write_text(render_openapi_schema())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
