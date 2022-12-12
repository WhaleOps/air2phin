from pathlib import Path
from typing import List

import pytest

from airphin.core.rules.loader import all_rules
from airphin.runner import with_str
from airphin.utils.file import read_yaml

rules_dir = Path(__file__).parent
test_cases_rules: List[Path] = list(rules_dir.glob("*.yaml"))

FLAG_EXAMPLES = "examples"
FLAG_TEST_CASE = "test_cases"
FLAG_SRC = "src"
FLAG_DEST = "dest"


@pytest.mark.parametrize("rule_ex", all_rules())
def test_rules_example(rule_ex: Path) -> None:
    contents = read_yaml(rule_ex)
    cases = contents.get(FLAG_EXAMPLES)
    for name, case in cases.items():
        src = case.get(FLAG_SRC)
        dest = case.get(FLAG_DEST)
        assert dest == with_str(src), f"Migrate test case {rule_ex.stem}.{name} failed."


@pytest.mark.parametrize("rule_ex", test_cases_rules)
def test_test_rules_example(rule_ex: Path) -> None:
    contents = read_yaml(rule_ex)
    cases = contents.get(FLAG_TEST_CASE)
    for name, case in cases.items():
        src = case.get(FLAG_SRC)
        dest = case.get(FLAG_DEST)
        assert dest == with_str(src), f"Migrate test case {rule_ex.stem}.{name} failed."
