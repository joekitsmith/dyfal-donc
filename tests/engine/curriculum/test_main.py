from pathlib import Path

import pytest

from engine.curriculum.__main__ import main
from tests.engine.curriculum.conftest import CurriculumWriter


class TestCli:
    def test_ok(
        self, write_curriculum: CurriculumWriter, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main([str(write_curriculum())]) == 0
        out = capsys.readouterr().out
        assert out.index("lex:siarad") < out.index("pat:dw-in")
        assert "OK: 2 items" in out

    def test_error(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([str(tmp_path)]) == 1
        assert "error: missing file" in capsys.readouterr().err

    def test_usage(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([]) == 2
        assert "usage" in capsys.readouterr().err
