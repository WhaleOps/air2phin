import ast
from _ast import With, ImportFrom, Call, Assign
from typing import Any

from airtolphin.rules.rule_bash import Bash
from airtolphin.rules.rule_dag import Dag
from airtolphin.rules.rule_imp import Package


class TransferVisitor(ast.NodeVisitor):
    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        Package(node).run()

    def visit_With(self, node: With) -> Any:
        for item in node.items:
            # DAG context
            expr = item.context_expr
            if isinstance(expr, Call):
                Dag(expr).run()
        for body in node.body:
            if isinstance(body, Assign):
                value = body.value
                # Operator type
                if isinstance(value, Call):
                    Bash(value).run()

    def visit_Call(self, node: Call) -> Any:
        Dag(node).run()
        Bash(node).run()
