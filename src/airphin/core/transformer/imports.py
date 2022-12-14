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
from airphin.core.rules.config import Config, ImportConfig


class ImportTransformer(cst.CSTTransformer):
    """CST Transformer for airflow operators."""

    def __init__(self, config: Config):
        super().__init__()
        self.config: Config = config
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

    def visit_ImportFrom(self, node: cst.ImportFrom) -> Optional[bool]:
        # case ``from modules import class``
        if m.matches(node.module, m.TypeOf(m.Name)):
            self.mod_ref = node.module.value
        # case ``from package.module.[module1] import class``
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
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> Union[
        cst.BaseSmallStatement, FlattenSentinel[cst.BaseSmallStatement], RemovalSentinel
    ]:
        if self.mod_ref is not None:
            src_full_refs = [
                f"{self.mod_ref}.{class_name}" for class_name in self.class_names
            ]

            replaces = []
            adds = set()
            for full_ref in src_full_refs:
                if full_ref in self.config.imports:
                    dest: ImportConfig = self.config.imports[full_ref]
                    replaces.append(dest.replace.statement)
                    adds.update(dest.add)

            # get replace statement
            if len(replaces) == 0:
                return updated_node
            elif len(replaces) == 1:
                statement = replaces[0]
            else:
                class_name_only = [
                    stat.split(f" {TOKEN.IMPORT} ")[1] for stat in replaces[1:]
                ]
                statement = f"{TOKEN.COMMA} ".join(replaces[:1] + class_name_only)

            # Return replace and add statement
            # TODO, will use ; as separator of multiple statements, we should better use \n in the future
            return FlattenSentinel(
                [
                    *[cst.parse_statement(add).body[0] for add in adds],
                    cst.parse_statement(statement).body[0],
                ]
            )
        return updated_node
