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
from typing import Set, Union

import libcst as cst
import libcst.matchers as m
from libcst import BaseExpression, FlattenSentinel, RemovalSentinel
from libcst.metadata import PositionProvider, QualifiedName, QualifiedNameProvider

from airphin.core.rules.convertor import call_cov
from airphin.core.transformer.imports import ImportTransformer
from airphin.core.transformer.operators import OpTransformer


class Transformer(m.MatcherDecoratableTransformer):
    """CST Transformer from airflow to dolphinscheduler-sdk-python.

    The main class to call each rules to convert.
    """

    METADATA_DEPENDENCIES = (
        QualifiedNameProvider,
        PositionProvider,
    )

    def __init__(self):
        super().__init__()
        self._operator_cov = call_cov

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
            if qnp_name in call_cov:
                return updated_node.visit(OpTransformer(qnp_name))
        return updated_node

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> Union[
        cst.BaseSmallStatement, FlattenSentinel[cst.BaseSmallStatement], RemovalSentinel
    ]:
        """Convert from import statement."""
        return updated_node.visit(ImportTransformer())
