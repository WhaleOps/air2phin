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


class Operators:
    """Covert Airflow Operator to DolphinScheduler Task.

    :param node: The cst.Assign to be converted.
    """

    cst_attr_keep = ("whitespace_before_args",)

    call_attr_keep = ("dag",)

    def __init__(self, node: cst.Assign) -> None:
        self.node = node

    def run(self) -> cst.Assign:
        """Convert the cst.Assign statement."""
        # keep all cst.Call attribute which have to change
        call_kwargs = {}
        call_args = []
        call = cst.ensure_type(self.node.value, cst.Call)
        # TODO: UT on it ex: `common_path = Variable.get("common_path")`
        if isinstance(call.func, cst.Name):
            # covert `airflow.operators.bash.BashOperator` assign
            if cst.ensure_type(call.func, cst.Name).value == "BashOperator":
                call_kwargs["func"] = cst.Name("Shell")
                for arg in call.args:
                    arg_keyword = cst.ensure_type(arg.keyword, cst.Name).value
                    if arg_keyword == "task_id":
                        call_args.append(arg.with_changes(keyword=cst.Name("name")))
                    elif arg_keyword == "bash_command":
                        call_args.append(arg.with_changes(keyword=cst.Name("command")))
                    elif arg_keyword in self.call_attr_keep:
                        call_args.append(arg)
                call_kwargs["args"] = call_args
                for attr in self.cst_attr_keep:
                    call_kwargs[attr] = getattr(call, attr)
                return self.node.with_changes(value=cst.Call(**call_kwargs))
            # covert `airflow.operators.dummy` assign, dolphinscheduler without dummy operator so we use bash
            # task with `echo 'airflow dummy operator'`
            elif cst.ensure_type(call.func, cst.Name).value == "DummyOperator":
                call_kwargs["func"] = cst.Name("Shell")
                for arg in call.args:
                    arg_keyword = cst.ensure_type(arg.keyword, cst.Name).value
                    if arg_keyword == "task_id":
                        call_args.append(arg.with_changes(keyword=cst.Name("name")))

                        call_args.append(
                            cst.Arg(
                                keyword=cst.Name("command"),
                                value=cst.SimpleString(
                                    "\"echo 'airflow dummy operator'\""
                                ),
                            )
                        )
                    elif arg_keyword in self.call_attr_keep:
                        call_args.append(arg)
                call_kwargs["args"] = call_args
                for attr in self.cst_attr_keep:
                    call_kwargs[attr] = getattr(call, attr)
                return self.node.with_changes(value=cst.Call(**call_kwargs))
            # covert `SparkSqlOperator` assign
            elif cst.ensure_type(call.func, cst.Name).value == "SparkSqlOperator":
                call_kwargs["func"] = cst.Name("Sql")
                for arg in call.args:
                    arg_keyword = cst.ensure_type(arg.keyword, cst.Name).value
                    if arg_keyword == "task_id":
                        call_args.append(arg.with_changes(keyword=cst.Name("name")))
                    elif arg_keyword == "conn_id":
                        call_args.append(
                            arg.with_changes(keyword=cst.Name("datasource_name"))
                        )
                    elif arg_keyword == "sql":
                        call_args.append(arg)
                    elif arg_keyword in self.call_attr_keep:
                        call_args.append(arg)
                call_kwargs["args"] = call_args
                for attr in self.cst_attr_keep:
                    call_kwargs[attr] = getattr(call, attr)
                return self.node.with_changes(value=cst.Call(**call_kwargs))
            # TODO latest python operator had change to decorator
            # covert `PythonOperator` assign
            elif cst.ensure_type(call.func, cst.Name).value == "PythonOperator":
                call_kwargs["func"] = cst.Name("Python")
                for arg in call.args:
                    arg_keyword = cst.ensure_type(arg.keyword, cst.Name).value
                    if arg_keyword == "task_id":
                        call_args.append(arg.with_changes(keyword=cst.Name("name")))
                    elif arg_keyword == "python_callable":
                        call_args.append(
                            arg.with_changes(keyword=cst.Name("definition"))
                        )
                    elif arg_keyword in self.call_attr_keep:
                        call_args.append(arg)
                call_kwargs["args"] = call_args
                for attr in self.cst_attr_keep:
                    call_kwargs[attr] = getattr(call, attr)
                return self.node.with_changes(value=cst.Call(**call_kwargs))
        return self.node
