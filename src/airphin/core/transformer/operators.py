import copy
from typing import Optional, Sequence, Union

import libcst as cst
import libcst.matchers as m
from libcst import Arg, BaseExpression, FlattenSentinel, RemovalSentinel

from airphin.constants import TOKEN
from airphin.core.rules.config import CallConfig, Config, ParamDefaultConfig


class OpTransformer(cst.CSTTransformer):
    """CST Transformer for airflow operators.

    TODO Need to skip inner call like DAG(date_time=datetime.datetime.now().strftime("%Y-%m-%d"))

    :param qualified_name: qualified name of operator
    """

    def __init__(self, config: Config, qualified_name: Optional[str] = None):
        super().__init__()
        self._config: Config = config
        self.qualified_name = qualified_name
        assert self.qualified_name is not None
        self.visit_name = False
        self.migrated_param = set()

    @property
    def config(self) -> CallConfig:
        return self._config.calls.get(self.qualified_name)

    def matcher_op_name(self, node: cst.Name) -> bool:
        if self.visit_name is False and node.value == self.config.src_short:
            self.visit_name = True
            return True
        return False

    def match_replace_name(self, node: cst.Arg) -> bool:
        migrate_names = self.config.replace.keys()
        return m.matches(
            node,
            m.Arg(keyword=m.Name(m.MatchIfTrue(lambda name: name in migrate_names))),
        )

    def match_remove_name(self, node: cst.Arg) -> bool:
        return m.matches(
            node,
            m.Arg(
                keyword=m.Name(m.MatchIfTrue(lambda name: name in self.config.remove))
            ),
        )

    def leave_Name(
        self, original_node: cst.Name, updated_node: cst.Name
    ) -> "BaseExpression":
        if self.matcher_op_name(original_node):
            dest_name = self.config.short
            return updated_node.with_changes(value=dest_name)
        return updated_node

    def leave_Arg(
        self, original_node: cst.Arg, updated_node: cst.Arg
    ) -> Union[Arg, FlattenSentinel[cst.Arg], RemovalSentinel]:
        if self.match_replace_name(original_node):
            original_keyword = original_node.keyword.value
            dest_keyword = self.config.replace.get(original_keyword)

            self.migrated_param.add(dest_keyword)
            return updated_node.with_changes(keyword=cst.Name(value=dest_keyword))
        if self.match_remove_name(original_node):
            return cst.RemoveFromParent()
        return updated_node

    def _handle_missing_default(self, nodes: Sequence[cst.Arg]) -> Sequence[cst.Arg]:
        mutable = list(nodes)
        one_of = copy.deepcopy(mutable[-1])
        for arg in self.config.add.keys():
            default: ParamDefaultConfig = self.config.add.get(arg)

            if default.type == TOKEN.STRING:
                value = cst.SimpleString(value=f'"{default.value}"')
            elif default.type == TOKEN.CODE:
                value = cst.parse_expression(default.value)
            else:
                raise NotImplementedError
            mutable.append(
                one_of.with_changes(
                    value=value,
                    keyword=cst.Name(value=arg),
                )
            )
        return mutable

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> BaseExpression:
        if not self.config.add:
            return updated_node

        return updated_node.with_changes(
            args=self._handle_missing_default(updated_node.args)
        )
