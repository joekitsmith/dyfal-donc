import ast
import importlib
from pathlib import Path

import pytest

import api
import api.controllers as api_controllers
import api.schemas as api_schemas
import cymraeg
import engine
import persistence
import tts

CORE_PACKAGES = (cymraeg, engine)
BACKEND_PACKAGES = ("evals", "tools", "simulation", "api", "persistence", "tts")
SERVER_PACKAGES = ("api", "persistence", "tts")


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


PRIVATE_DATABASE_MODULES = (
    "persistence.database.models",
    "persistence.database.mappings",
)


def imported_modules(package_directory: Path) -> dict[Path, set[str]]:
    """The full names of the modules each source file imports.

    ``from persistence.database import models`` counts as importing
    ``persistence.database.models``.
    """
    imports: dict[Path, set[str]] = {}
    for path in sorted(package_directory.rglob("*.py")):
        names: set[str] = set()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module)
                names.update(f"{node.module}.{alias.name}" for alias in node.names)

        imports[path] = names

    return imports


def private_database_imports(package: object) -> list[str]:
    package_file = getattr(package, "__file__", None)
    assert package_file is not None
    return [
        f"{path} imports {name}"
        for path, names in imported_modules(Path(package_file).parent).items()
        for name in sorted(names)
        if any(
            name == private or name.startswith(f"{private}.")
            for private in PRIVATE_DATABASE_MODULES
        )
    ]


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

    @pytest.mark.parametrize("package", ("evals", "tools", "simulation"))
    def test_offline_tools_never_import_the_server(self, package: str) -> None:
        module = importlib.import_module(package)

        assert forbidden_imports(module, SERVER_PACKAGES) == []

    def test_persistence_never_imports_the_api(self) -> None:
        assert forbidden_imports(persistence, ("api",)) == []

    def test_persistence_never_imports_the_engine(self) -> None:
        assert forbidden_imports(persistence, ("engine", "cymraeg")) == []

    def test_the_api_reaches_the_speech_service_only_over_http(self) -> None:
        assert forbidden_imports(api, ("tts",)) == []

    def test_the_speech_service_imports_nothing_else_from_the_repository(self) -> None:
        assert (
            forbidden_imports(
                tts, ("api", "persistence", "engine", "cymraeg", "evals", "tools")
            )
            == []
        )

    def test_api_schemas_never_import_the_engine_or_persistence(self) -> None:
        assert (
            forbidden_imports(api_schemas, ("engine", "cymraeg", "persistence")) == []
        )

    def test_the_api_never_imports_the_tables_or_their_mappings(self) -> None:
        assert private_database_imports(api) == []

    def test_the_check_finds_a_table_import(self, tmp_path: Path) -> None:
        (tmp_path / "__init__.py").write_text(
            "from persistence.database import models\n"
        )
        (tmp_path / "module.py").write_text(
            "from persistence.database.models import Learner\n"
        )

        names = imported_modules(tmp_path)

        assert "persistence.database.models" in names[tmp_path / "__init__.py"]
        assert "persistence.database.models" in names[tmp_path / "module.py"]

    def test_api_controllers_never_import_fastapi(self) -> None:
        assert forbidden_imports(api_controllers, ("fastapi", "starlette")) == []

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
