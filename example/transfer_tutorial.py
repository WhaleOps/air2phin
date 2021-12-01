import libcst as cst

from airtolphin.core.transformer import CSTTransformer

with open("./airflow/tutorial.py") as f:
    data = f.read()

    parse_cst = cst.parse_module(data)
    # print(parse_cst)
    print(parse_cst.visit(CSTTransformer()).code)
