import ast
from pathlib import Path

import cymraeg


class TestPackageBoundary:
    def test_cymraeg_never_imports_engine(self) -> None:
        package_directory = Path(cymraeg.__file__).parent
        for path in package_directory.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                names = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else []
                )
                assert not any(name.split(".")[0] == "engine" for name in names), path
