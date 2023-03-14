# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import warnings
from typing import List, Set, Union

import libcst as cst
import libcst.matchers as m
from libcst import BaseExpression, FlattenSentinel, RemovalSentinel, SimpleStatementLine
from libcst.metadata import PositionProvider, QualifiedName, QualifiedNameProvider

from air2phin.constants import Keyword
from air2phin.core.rules.config import Config
from air2phin.core.transformer.imports import ImportTransformer
from air2phin.core.transformer.operators import OpTransformer


class Transformer(cst.CSTTransformer):
    """CST Transformer route class from airflow to dolphinscheduler-sdk-python.

    The main class to call each rules to migrate, just like a router, currently will route to `imports` and
    `operators` transformer.

    :param config: libCST transformer configuration, use it to get importer and callable migrate setting.
    """

    METADATA_DEPENDENCIES = (
        QualifiedNameProvider,
        PositionProvider,
    )

    def __init__(self, config: Config):
        super().__init__()
        self.config: Config = config
        self.workflow_alias = set()
        self.have_submit_expr = set()

    @staticmethod
    def _get_qualified_name(qualifie: Set[QualifiedName]) -> str:
        if len(qualifie) > 1:
            warnings.warn(
                "QualifiedNameProvider get more than one qualified name, will use the first one.",
                RuntimeWarning,
            )
        for q in qualifie:
            return q.name

    # @m.call_if_inside(
    #     m.Call(
    #         func=m.MatchMetadataIfTrue(
    #             meta.QualifiedNameProvider,
    #             lambda qualnames: any(
    #                 n.name in call_cov for n in qualnames
    #             ),
    #         )
    #     )
    # )
    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> BaseExpression:
        qnp = self.get_metadata(QualifiedNameProvider, original_node)
        if qnp:
            qnp_name = self._get_qualified_name(qnp)
            if qnp_name in self.config.calls:
                return updated_node.visit(OpTransformer(self.config, qnp_name))
        return updated_node

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> Union[
        cst.BaseSmallStatement, FlattenSentinel[cst.BaseSmallStatement], RemovalSentinel
    ]:
        """Migrate from import statement."""
        return updated_node.visit(ImportTransformer(self.config))

    def leave_WithItem_asname(self, node: cst.WithItem) -> None:
        """Get airflow Dags alias names."""
        if m.matches(node.item, m.Call()) and m.matches(
            cst.ensure_type(node.item, cst.Call).func,
            m.Name(value=Keyword.AIRFLOW_DAG_SIMPLE),
        ):
            self.workflow_alias.add(node.asname.name.value)

    def leave_Expr(
        self, original_node: cst.Expr, updated_node: cst.Expr
    ) -> Union[
        cst.BaseSmallStatement,
        cst.FlattenSentinel[cst.BaseSmallStatement],
        RemovalSentinel,
    ]:
        """Update workflow ``alias.submit()`` expr exits or not statement."""
        if m.matches(
            original_node.value,
            m.Call(
                func=m.Attribute(
                    value=m.OneOf(*[m.Name(a) for a in self.workflow_alias]),
                    attr=m.Name(Keyword.WORKFLOW_SUBMIT),
                )
            ),
        ):
            self.have_submit_expr.add(original_node.value.func.value.value)
        return updated_node

    def _build_submit_exprs(self) -> List[SimpleStatementLine]:
        miss_alias = self.workflow_alias.difference(self.have_submit_expr)
        return [
            cst.parse_statement(f"{alias}.{Keyword.WORKFLOW_SUBMIT}()")
            for alias in miss_alias
        ]

    def _build_marco_path_exprs(self) -> List[SimpleStatementLine]:
        return [
            cst.parse_statement(Keyword.WORKFLOW_MARCO_PATH_FMT.format(wf=alias))
            for alias in self.workflow_alias
        ]

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        if self.have_submit_expr == self.workflow_alias:
            return updated_node

        # add submit expr when do not have
        body_with_submit = list(updated_node.body)
        body_with_submit.extend(self._build_marco_path_exprs())
        body_with_submit.extend(self._build_submit_exprs())
        return updated_node.with_changes(body=body_with_submit)
