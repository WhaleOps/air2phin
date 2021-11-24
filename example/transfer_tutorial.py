import ast

from airtolphin.core.transfer_visitor import TransferVisitor

with open("./airflow/tutorial.py") as f:
    data = f.read()

    ast_parser = ast.parse(data)
    TransferVisitor().visit(ast_parser)

    print(ast.unparse(ast_parser))
