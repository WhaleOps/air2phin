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
from typing import Optional, Sequence, Union

import libcst as cst
import libcst.matchers as m
from libcst import FlattenSentinel, RemovalSentinel

from airphin.constants import TOKEN
from airphin.core.rules.convertor import imp_cov


class ImportTransformer(cst.CSTTransformer):
    def __init__(self):
        super().__init__()
        self.mod_ref = None
        self.class_names = []

    def _get_attr_nested_value(self, node: cst.Attribute) -> str:
        if m.matches(node.value, m.TypeOf(m.Name)):
            return f"{node.value.value}.{node.attr.value}"
        elif m.matches(node.value, m.TypeOf(m.Attribute)):
            nested = self._get_attr_nested_value(
                cst.ensure_type(node.value, cst.Attribute)
            )
            return f"{nested}.{node.attr.value}"

    def visit_ImportFrom(self, node: "ImportFrom") -> Optional[bool]:
        if m.matches(node.module, m.TypeOf(m.Name)):
            self.mod_ref = node.module.value
        elif m.matches(node.module, m.TypeOf(m.Attribute)):
            self.mod_ref = self._get_attr_nested_value(
                cst.ensure_type(node.module, cst.Attribute)
            )

        # skip ``import *``, aka ImportStar
        if isinstance(node.names, Sequence):
            self.class_names = [
                cst.ensure_type(ia, cst.ImportAlias).name.value for ia in node.names
            ]
        return False

    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> Union[
        "BaseSmallStatement", FlattenSentinel["BaseSmallStatement"], RemovalSentinel
    ]:
        if self.mod_ref is not None:
            src_full_refs = [
                f"{self.mod_ref}.{class_name}" for class_name in self.class_names
            ]
            # convert new statements
            statements = [
                imp_cov.get(full_ref).statement
                for full_ref in src_full_refs
                if full_ref in imp_cov
            ]
            if len(statements) == 1:
                return cst.parse_statement(statements[0]).body[0]
            elif len(statements) > 1:
                class_name_only = [
                    stat.split(f" {TOKEN.IMPORT} ")[1] for stat in statements[1:]
                ]
                statement = f"{TOKEN.COMMA} ".join(statements[:1] + class_name_only)
                return cst.parse_statement(statement).body[0]
        return updated_node
