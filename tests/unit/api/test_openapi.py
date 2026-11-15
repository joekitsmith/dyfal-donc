import json
from pathlib import Path

from api.openapi import main, render_openapi_schema

REPOSITORY_ROOT = Path(__file__).parents[3]


class TestRenderOpenapiSchema:
    def test_describes_the_audio_account_and_learner_paths(self) -> None:
        paths = json.loads(render_openapi_schema())["paths"]

        assert "/exercises/{exercise_id}/audio/{track}" in paths
        assert "/auth/guest" in paths
        assert "/me/next" in paths
        assert not any(path.startswith("/learners") for path in paths)

    def test_issuing_an_exercise_is_not_a_get(self) -> None:
        paths = json.loads(render_openapi_schema())["paths"]

        assert set(paths["/me/next"]) == {"post"}

    def test_is_stable_between_calls(self) -> None:
        assert render_openapi_schema() == render_openapi_schema()


class TestCommittedSchema:
    def test_matches_the_api(self) -> None:
        committed = (REPOSITORY_ROOT / "frontend" / "openapi.json").read_text()

        assert committed == render_openapi_schema(), "Run `make web-types`"


class TestMain:
    def test_writes_the_schema_to_the_path(self, tmp_path: Path) -> None:
        path = tmp_path / "openapi.json"

        assert main((str(path),)) == 0
        assert path.read_text() == render_openapi_schema()

    def test_needs_exactly_one_path(self) -> None:
        assert main(()) == 2
