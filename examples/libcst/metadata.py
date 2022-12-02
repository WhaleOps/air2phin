"""source code copy-paste from https://libcst.readthedocs.io/en/latest/metadata_tutorial.html"""
from typing import Optional

import libcst as cst
from libcst.metadata import PositionProvider, QualifiedNameProvider


class IsParamProvider(cst.BatchableMetadataProvider[bool]):
    """
    Marks Name nodes found as a parameter to a function.
    """

    def __init__(self) -> None:
        super().__init__()
        self.is_param = False

    def visit_Param(self, node: cst.Param) -> None:
        # Mark the child Name node as a parameter
        self.set_metadata(node.name, True)

    def visit_Name(self, node: cst.Name) -> None:
        # Mark all other Name nodes as not parameters
        if not self.get_metadata(type(self), node, False):
            self.set_metadata(node, False)


# module = cst.parse_module("x")
# wrapper = cst.MetadataWrapper(module)
#
# isparam = wrapper.resolve(IsParamProvider)
# x_name_node = wrapper.module.body[0].body[0].value

# print(isparam[x_name_node])


class ParamPrinter(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (
        IsParamProvider,
        PositionProvider,
        QualifiedNameProvider,
    )

    def visit_Call(self, node: cst.Call) -> Optional[bool]:
        # Only print out names that are parameters
        if self.get_metadata(QualifiedNameProvider, node):
            pos = self.get_metadata(PositionProvider, node).start
            print(f"found at line {pos.line}, column {pos.column}")

        return super().visit_Call(node)

    def visit_Name(self, node: cst.Name) -> None:
        # Only print out names that are parameters
        if self.get_metadata(IsParamProvider, node):
            pos = self.get_metadata(PositionProvider, node).start
            print(f"{node.value} found at line {pos.line}, column {pos.column}")


module = cst.parse_module(
    "from datetime import datetime\n\ndef foo(x):\n    y = 1\n    now = datetime.now()\n    return x + y"
)
wrapper = cst.MetadataWrapper(module)
result = wrapper.visit(ParamPrinter())  # NB: wrapper.visit not module.visit
