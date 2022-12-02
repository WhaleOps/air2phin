import copy
from typing import Optional, Sequence, Union

import libcst as cst
import libcst.matchers as m
from libcst import Arg, BaseExpression, FlattenSentinel, RemovalSentinel

from airphin.core.rules.convertor import call_cov


class OpTransformer(cst.CSTTransformer):
    """CST Transformer for operators.

    TODO Need to skip inner call like DAG(date_time=datetime.datetime.now().strftime("%Y-%m-%d"))
    """

    def __init__(self, qualified_name: Optional[str] = None):
        super().__init__()
        self.qualified_name = qualified_name
        self.visit_name = False
        self.converted_param = set()
        assert self.qualified_name is not None
        self.cov_map = call_cov.get(self.qualified_name)

    def matcher_op_name(self, node: cst.Name) -> bool:
        if self.visit_name is False and node.value == self.cov_map.src_short:
            self.visit_name = True
            return True
        return False

    def matcher_param_name(self, node: cst.Arg) -> bool:
        convert_names = self.cov_map.param.keys()
        return m.matches(
            node,
            m.Arg(keyword=m.Name(m.MatchIfTrue(lambda name: name in convert_names))),
        )

    def leave_ImportFrom(
        self, original_node: "ImportFrom", updated_node: "ImportFrom"
    ) -> Union[
        "BaseSmallStatement", FlattenSentinel["BaseSmallStatement"], RemovalSentinel
    ]:
        if self.matcher_import_name(original_node):
            dest_module = self.cov_map.module
            return updated_node.with_changes(module=cst.Name(value=dest_module))
        return updated_node

    def leave_Name(
        self, original_node: "Name", updated_node: "Name"
    ) -> "BaseExpression":
        if self.matcher_op_name(original_node):
            dest_name = self.cov_map.short
            return updated_node.with_changes(value=dest_name)
        return updated_node

    def leave_Arg(
        self, original_node: "Arg", updated_node: "Arg"
    ) -> Union[Arg, FlattenSentinel["Arg"], RemovalSentinel]:
        if self.matcher_param_name(original_node):
            original_keyword = original_node.keyword.value
            dest_keyword = self.cov_map.param.get(original_keyword)

            self.converted_param.add(dest_keyword)
            # also change to default value when have ``default`` node
            if dest_keyword is self.cov_map.default:
                default_value: str = self.cov_map.default.get(dest_keyword)
                return updated_node.with_changes(
                    keyword=cst.Name(value=dest_keyword),
                    value=cst.SimpleString(value=default_value),
                )

            return updated_node.with_changes(keyword=cst.Name(value=dest_keyword))
        return updated_node

    def _handle_missing_default(self, nodes: Sequence[cst.Arg]) -> Sequence[cst.Arg]:
        miss_default = self.cov_map.default.keys() - self.converted_param
        if not miss_default:
            return nodes

        mutable = list(nodes)
        one_of = copy.deepcopy(mutable[-1])
        for miss in miss_default:
            value = self.cov_map.default.get(miss)

            mutable.append(
                one_of.with_changes(
                    value=cst.SimpleString(value=f'"{value}"'),
                    keyword=cst.Name(value=miss),
                )
            )
        return mutable

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> BaseExpression:
        if not self.cov_map.default:
            return updated_node

        return updated_node.with_changes(
            args=self._handle_missing_default(updated_node.args)
        )
