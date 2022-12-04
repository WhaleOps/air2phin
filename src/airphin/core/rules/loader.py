from pathlib import Path
from typing import List

project = Path(__file__).parent.parent.parent

path_rule = project.joinpath("rules")
path_operators = path_rule.joinpath("operators")
path_dag_cnx = path_rule.joinpath("core", "dagContext.yaml")


def all_rules() -> List[Path]:
    """Get all rules in airphin.rules directory."""
    return [path for path in path_rule.glob("**/*") if path.is_file()]
