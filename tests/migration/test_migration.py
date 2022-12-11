from pathlib import Path
from typing import List

import pytest

from airphin.runner import with_str
from airphin.utils.file import read_yaml

migration_dir = Path(__file__).parent
test_cases: List[Path] = list(migration_dir.glob("*.yaml"))

FLAG_MIGRATION = "migration"
FLAG_SRC = "src"
FLAG_DEST = "dest"


@pytest.mark.parametrize("path", test_cases)
def test_migration(path: Path) -> None:
    contents = read_yaml(path)
    cases = contents.get(FLAG_MIGRATION)
    for name, case in cases.items():
        src = case.get(FLAG_SRC)
        dest = case.get(FLAG_DEST)
        assert dest == with_str(src), f"Migrate test case {path.stem}.{name} failed."
