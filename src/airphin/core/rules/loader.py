from pathlib import Path

project = Path(__file__).parent.parent.parent

path_rule = project.joinpath("rules")
path_operators = path_rule.joinpath("operators")
path_dag_cnx = path_rule.joinpath("core", "dagContext.yaml")


def all_rules() -> list[Path]:
    return [path for path in path_rule.glob("**/*") if path.is_file()]
