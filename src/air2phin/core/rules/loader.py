from pathlib import Path
from typing import List

project = Path(__file__).parent.parent.parent

path_rule = project.joinpath("rules")
path_operators = path_rule.joinpath("operators")
path_hooks = path_rule.joinpath("hooks")
path_dag_cnx = path_rule.joinpath("core", "dagContext.yaml")

rule_imports = [path_dag_cnx, path_operators, path_hooks]

rule_calls = [
    path_dag_cnx,
    path_operators,
    path_hooks,
]


def build_in_rules() -> List[Path]:
    """Get all build-in rules in air2phin.rules directory."""
    return [path for path in path_rule.glob("**/*") if path.is_file()]
