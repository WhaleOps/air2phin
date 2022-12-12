from pathlib import Path
from typing import List

import pytest

from airphin.core.rules.loader import build_in_rules
from airphin.core.rules.config import Config
from airphin.runner import Runner
from airphin.utils.file import read_yaml
from airphin.constants import CONFIG

rules_dir = Path(__file__).parent
test_cases_rules: List[Path] = list(rules_dir.glob("*.yaml"))

FLAG_TEST_CASE = "test_cases"


@pytest.mark.parametrize("rule_ex", build_in_rules())
def test_rules_example(rule_ex: Path) -> None:
    runner = Runner(Config())
    contents = read_yaml(rule_ex)
    cases = contents.get(CONFIG.EXAMPLE)
    for name, case in cases.items():
        src = case.get(CONFIG.SOURCE)
        dest = case.get(CONFIG.DESTINATION)
        assert dest == runner.with_str(src), f"Migrate test case {rule_ex.stem}.{name} failed."


@pytest.mark.parametrize("rule_ex", test_cases_rules)
def test_test_rules_example(rule_ex: Path) -> None:
    runner = Runner(Config())
    contents = read_yaml(rule_ex)
    cases = contents.get(FLAG_TEST_CASE)
    for name, case in cases.items():
        src = case.get(CONFIG.SOURCE)
        dest = case.get(CONFIG.DESTINATION)
        assert dest == runner.with_str(src), f"Migrate test case {rule_ex.stem}.{name} failed."

