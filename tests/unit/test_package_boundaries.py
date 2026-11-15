import ast
from pathlib import Path

import pytest

import cymraeg
import engine

CORE_PACKAGES = (cymraeg, engine)
BACKEND_PACKAGES = ("evals", "tools", "simulation")


def imported_top_level_modules(package_directory: Path) -> dict[Path, set[str]]:
    """The top-level module names each source file under the directory imports."""
    imports: dict[Path, set[str]] = {}
    for path in sorted(package_directory.rglob("*.py")):
        names: set[str] = set()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.split(".")[0])

        imports[path] = names

    return imports


def forbidden_imports(package: object, forbidden: tuple[str, ...]) -> list[str]:
    package_file = getattr(package, "__file__", None)
    assert package_file is not None
    return [
        f"{path} imports {name}"
        for path, names in imported_top_level_modules(Path(package_file).parent).items()
        for name in sorted(names & set(forbidden))
    ]


class TestPackageBoundaries:
    def test_cymraeg_never_imports_engine(self) -> None:
        assert forbidden_imports(cymraeg, ("engine",)) == []

    @pytest.mark.parametrize(
        "package", CORE_PACKAGES, ids=lambda package: package.__name__
    )
    def test_core_never_imports_backend(self, package: object) -> None:
        assert forbidden_imports(package, BACKEND_PACKAGES) == []

    def test_only_one_learner_module_imports_fsrs(self) -> None:
        engine_file = engine.__file__
        assert engine_file is not None

        importers = [
            path.name
            for path, names in imported_top_level_modules(
                Path(engine_file).parent
            ).items()
            if "fsrs" in names
        ]

        assert importers == ["fsrs_model.py"]

    def test_the_check_finds_a_forbidden_import(self, tmp_path: Path) -> None:
        (tmp_path / "module.py").write_text("from engine.curriculum import Lexeme\n")

        imports = imported_top_level_modules(tmp_path)

        assert imports == {tmp_path / "module.py": {"engine"}}

    def test_relative_imports_are_not_counted(self, tmp_path: Path) -> None:
        (tmp_path / "module.py").write_text("from . import sibling\n")

        assert imported_top_level_modules(tmp_path) == {tmp_path / "module.py": set()}
