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

from typing import Union

import libcst as cst
from libcst import FlattenSentinel, RemovalSentinel

from airtolphin.rules.dag_context import DAGContext
from airtolphin.rules.import_from import From
from airtolphin.rules.operators import Operators


class CSTTransformer(cst.CSTTransformer):
    """CST Transformer from airflow to dolphinscheduler-sdk-python.

    The main class to call each rules to convert.
    """

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
