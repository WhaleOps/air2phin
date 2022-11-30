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

import libcst as cst


class From:
    """Covert import from statement.

    :param node: The cst.ImportFrom to be converted.
    """

    def __init__(self, node: cst.ImportFrom):
        self.node = node

    def run(self) -> cst.ImportFrom:
        """Convert the cst.ImportFrom statement."""
        module = self.node.module
        if isinstance(module, cst.Attribute):
            # covert `airflow.operators.bash` or `airflow.operators.(dummy_operator|dummy)`,
            # we here covert dummy operator to bash operator with command `echo 'airflow dummy operator'`
            # cause dolphinscheduler do not support Task like dummy operator.
            if (
                module.attr.value in ("bash", "dummy_operator", "dummy")
                and module.value.attr.value == "operators"
            ):
                self.node = self.node.with_changes(
                    module=cst.Attribute(
                        cst.Attribute(
                            cst.Name("pydolphinscheduler"),
                            cst.Name("tasks"),
                        ),
                        cst.Name("shell"),
                    )
                )
            # covert `airflow.operators.spark_sql_operator`
            if (
                module.attr.value == "spark_sql_operator"
                and module.value.attr.value == "operators"
            ):
                self.node = self.node.with_changes(
                    module=cst.Attribute(
                        cst.Attribute(
                            cst.Name("pydolphinscheduler"),
                            cst.Name("tasks"),
                        ),
                        cst.Name("sql"),
                    )
                )
            # covert `airflow.operators.python_operator`
            if (
                module.attr.value == "python_operator"
                and module.value.attr.value == "operators"
            ):
                self.node = self.node.with_changes(
                    module=cst.Attribute(
                        cst.Attribute(
                            cst.Name("pydolphinscheduler"),
                            cst.Name("tasks"),
                        ),
                        cst.Name("python"),
                    )
                )
        elif isinstance(module, cst.Name):
            # covert `airflow`
            if module.value == "airflow":
                self.node = self.node.with_changes(
                    module=cst.Attribute(
                        cst.Attribute(
                            cst.Name("pydolphinscheduler"),
                            cst.Name("core"),
                        ),
                        cst.Name("process_definition"),
                    )
                )
        for import_alias in self.node.names:
            # covert `DAG`
            if import_alias.name.value == "DAG":
                self.node = self.node.with_changes(
                    names=(cst.ImportAlias(cst.Name("ProcessDefinition")),)
                )
            # covert `BashOperator` and `DummyOperator`
            if import_alias.name.value in ("BashOperator", "DummyOperator"):
                self.node = self.node.with_changes(
                    names=(cst.ImportAlias(cst.Name("Shell")),)
                )
            elif import_alias.name.value == "SparkSqlOperator":
                self.node = self.node.with_changes(
                    names=(cst.ImportAlias(cst.Name("Sql")),)
                )
            elif import_alias.name.value == "PythonOperator":
                self.node = self.node.with_changes(
                    names=(cst.ImportAlias(cst.Name("Python")),)
                )
        return self.node
