from pathlib import Path
from typing import List

import pytest

from air2phin.constants import ConfigKey
from air2phin.core.rules.config import Config
from air2phin.core.rules.loader import build_in_rules
from air2phin.runner import Runner
from air2phin.utils.file import read_yaml

rules_dir = Path(__file__).parent
test_cases_rules: List[Path] = list(rules_dir.glob("*.yaml"))

FLAG_TEST_CASE = "test_cases"


@pytest.mark.parametrize("rule_ex", build_in_rules())
def test_rules_example(rule_ex: Path) -> None:
    runner = Runner(Config())
    contents = read_yaml(rule_ex)
    cases = contents.get(ConfigKey.EXAMPLE)
    for name, case in cases.items():
        src = case.get(ConfigKey.SOURCE)
        dest = case.get(ConfigKey.DESTINATION)
        assert (
            runner.with_str(src) == dest
        ), f"Migrate test case {rule_ex.stem}.{name} failed."


@pytest.mark.parametrize("rule_ex", test_cases_rules)
def test_test_rules_example(rule_ex: Path) -> None:
    runner = Runner(Config())
    contents = read_yaml(rule_ex)
    cases = contents.get(FLAG_TEST_CASE)
    for name, case in cases.items():
        src = case.get(ConfigKey.SOURCE)
        dest = case.get(ConfigKey.DESTINATION)
        assert dest == runner.with_str(
            src
        ), f"Migrate test case {rule_ex.stem}.{name} failed."
