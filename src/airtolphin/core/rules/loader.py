from pathlib import Path

root = Path(__file__).parent.parent.parent.parent.parent
src = root.joinpath("src")

path_rule = src.joinpath("airtolphin", "rules")
path_operators = path_rule.joinpath("operators")
path_dag_cnx = path_rule.joinpath("core", "dagContext.yaml")
