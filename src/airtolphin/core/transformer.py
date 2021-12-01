from typing import Union

import libcst as cst
from libcst import FlattenSentinel, RemovalSentinel

from airtolphin.rules.dag_context import DAGContext
from airtolphin.rules.operators import Operators
from airtolphin.rules.import_from import From


class CSTTransformer(cst.CSTTransformer):

    def leave_ImportFrom(
            self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> Union[
        cst.BaseSmallStatement, FlattenSentinel[cst.BaseSmallStatement], RemovalSentinel
    ]:
        """Covert from import statement."""
        return From(updated_node).run()

    def leave_WithItem(
            self, original_node: cst.WithItem, updated_node: cst.WithItem
    ) -> Union[cst.WithItem, FlattenSentinel[cst.WithItem], RemovalSentinel]:
        """Covert `with DAG(...) as dag` context."""
        return DAGContext(updated_node).run()

    def leave_Assign(
            self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> Union[
        cst.BaseSmallStatement, FlattenSentinel[cst.BaseSmallStatement], RemovalSentinel
    ]:
        """Covert `airflow.operators` assign.

        For now it only support bash operator.
        """
        if isinstance(updated_node.value, cst.Call):
            return Operators(updated_node).run()
        return updated_node
