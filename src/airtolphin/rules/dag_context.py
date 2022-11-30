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


class DAGContext:
    """Convert DAG context statement.

    :param node: The cst.WithItem to be converted.
    """

    args_white_list_map = {
        "description": "description",
        "start_date": "start_time",
        "schedule_interval": "schedule",
    }

    def __init__(self, node: cst.WithItem):
        self.node = node

    def run(self) -> cst.WithItem:
        """Convert the cst.WithItem statement."""
        item = self.node.item
        if hasattr(item, "func") and isinstance(item.func, cst.Name):
            if item.func.value == "DAG":
                update_func = cst.Name("ProcessDefinition")

                args = cst.ensure_type(item, cst.Call).args
                update_args = []

                for key, arg in enumerate(args):
                    if key == 0 and arg.keyword is None:
                        update_args.append(arg)
                    elif (
                        arg.keyword is not None
                        and arg.keyword.value in self.args_white_list_map
                    ):
                        keyword_name = cst.ensure_type(arg.keyword, cst.Name).value
                        new_name = self.args_white_list_map[keyword_name]
                        update_args.append(arg.with_changes(keyword=cst.Name(new_name)))
                return self.node.with_changes(
                    item=cst.Call(
                        func=update_func,
                        args=tuple(update_args),
                    )
                )
        return self.node
