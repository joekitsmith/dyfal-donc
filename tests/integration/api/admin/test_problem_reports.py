import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from tests.integration.api.helpers import start_guest
from api.admin.problem_reports import main


@pytest.fixture(autouse=True)
def database(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", engine.url.render_as_string(hide_password=False))


def send(client: TestClient, description: str, category: str = "grammar") -> None:
    response = client.post(
        "/me/problem-reports",
        json={"source": "general", "category": category, "description": description},
    )
    assert response.status_code == 204


class TestProblemReportsCommand:
    def test_lists_resolves_and_lists_again(
        self, client: TestClient, capsys: pytest.CaptureFixture[str]
    ) -> None:
        start_guest(client)
        send(client, "First")
        send(client, "Second", category="mutation")

        main([])
        listed = capsys.readouterr().out
        main(["--resolve", "1"])
        capsys.readouterr()
        main([])
        after = capsys.readouterr().out
        main(["--all"])
        everything = capsys.readouterr().out

        assert listed.index("First") < listed.index("Second")
        assert "First" not in after
        assert "Second" in after
        assert "(resolved)" in everything

    def test_resolving_an_unknown_report_exits_with_a_message(self) -> None:
        with pytest.raises(SystemExit, match="Problem report 7 does not exist"):
            main(["--resolve", "7"])

    def test_all_and_resolve_do_not_go_together(self) -> None:
        with pytest.raises(SystemExit, match="cannot be used together"):
            main(["--all", "--resolve", "1"])
