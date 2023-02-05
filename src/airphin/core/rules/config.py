from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

from airphin.constants import CONFIG, REGEXP, TOKEN
from airphin.core.rules.loader import rule_calls, rule_imports
from airphin.utils.file import read_multi_yaml, read_yaml


class ParamDefaultConfig(NamedTuple):
    """Default statement config."""

    type: str
    value: str


class CallConfig(NamedTuple):
    """Call config."""

    long: str
    short: str
    src_long: str
    src_short: str
    replace: Dict[str, str]
    add: Dict[str, ParamDefaultConfig]
    remove: List[str]


class ImportStatementConfig(NamedTuple):
    """Import replace statement config."""

    inner_val: str
    inner_attr: str
    attr: str
    name: str
    statement: str


class ImportConfig(NamedTuple):
    """Import config."""

    replace: ImportStatementConfig
    add: List[str]
    remove: List[str]


class Config:
    """Configurations of airphin, including all configs change behavior of airphin.

    :param customs: User custom path of rules, can overwrite build-in rules.
    :param inplace: Replace source python file inplace instread of create a new file.
    :param imports: Build-in imports rules path.
    :param calls: Build-in call rules path.
    """

    def __init__(
        self,
        customs: Optional[List[Path]] = None,
        inplace: Optional[bool] = False,
        imports: Optional[List[Path]] = rule_imports,
        calls: Optional[List[Path]] = rule_calls,
    ):
        self._customs = customs
        self.inplace = inplace
        self._imports = imports
        self._calls = calls

    @property
    def imports_path(self) -> List[Path]:
        """Get all imports path from rules."""
        if not self._customs:
            return self._imports
        self._imports.extend(self._customs)
        return self._imports

    @property
    def imports(self) -> Dict[str, ImportConfig]:
        """Get all import migrator from rules."""
        return self.imp_migrator()

    @property
    def calls_path(self) -> List[Path]:
        """Get all call rules path."""
        if not self._customs:
            return self._calls
        self._calls.extend(self._customs)
        return self._calls

    @property
    def calls(self) -> Dict[str, CallConfig]:
        """Get all call migrator from rules."""
        return self.call_migrator()

    @staticmethod
    def _build_caller(
        src: str, dest: str, parameters: List[Dict[str, Any]]
    ) -> CallConfig:
        return CallConfig(
            long=dest,
            short=dest.split(TOKEN.POINT)[-1],
            src_long=src,
            src_short=src.split(TOKEN.POINT)[-1],
            replace={
                p[CONFIG.SOURCE]: p[CONFIG.DESTINATION]
                for p in parameters
                if p[CONFIG.ACTION] == CONFIG.KW_REPLACE
            },
            add={
                p[CONFIG.ARGUMENT]: ParamDefaultConfig(
                    type=p[CONFIG.DEFAULT][CONFIG.TYPE],
                    value=p[CONFIG.DEFAULT][CONFIG.VALUE],
                )
                for p in parameters
                if p[CONFIG.ACTION] == CONFIG.KW_ADD
            },
            remove=[
                p[CONFIG.ARGUMENT]
                for p in parameters
                if p[CONFIG.ACTION] == CONFIG.KW_REMOVE
            ],
        )

    @staticmethod
    def _handle_rules_path(*args) -> List[Dict[str, Any]]:
        for arg in args:
            if arg.is_file():
                content: Dict = read_yaml(arg)
                yield content
            if arg.is_dir():
                contents: List[Dict] = read_multi_yaml(arg.glob(REGEXP.PATH_YAML))
                for content in contents:
                    yield content

    @staticmethod
    def get_module_action(
        migration: Dict[str, Any], action_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific action type from rules.

        :param migration: Config Migration node.
        :param action_type: Action type, can be `add`, `remove`, `replace`.
        """
        actions = [
            action
            for action in migration[CONFIG.MODULE]
            if action[CONFIG.ACTION] == action_type
        ]
        if len(actions) > 1:
            raise ValueError("Each type of action can only have one.")
        return actions[0] if actions else None

    def call_migrator(self) -> Dict[str, CallConfig]:
        """Get all call migrator from rules."""
        migrator = {}

        for content in self._handle_rules_path(*self.calls_path):
            migration = content[CONFIG.MIGRATION]
            parameters = migration[CONFIG.PARAMETER]
            replace = self.get_module_action(migration, CONFIG.KW_REPLACE)
            src = replace[CONFIG.SOURCE]
            dest = replace[CONFIG.DESTINATION]

            if isinstance(src, str):
                migrator[src] = self._build_caller(src, dest, parameters)
            elif isinstance(src, list):
                for inner_src in src:
                    migrator[inner_src] = self._build_caller(
                        inner_src, dest, parameters
                    )
            else:
                raise RuntimeError("Invalid migration.module.src type: %s" % type(src))
        return migrator

    # TODO: make it can use in any number module import statemant
    @staticmethod
    def _build_replace_importer(action: Dict[str, Any]) -> ImportStatementConfig:
        dest = action[CONFIG.DESTINATION]
        inner_val, inner_attr, attr, name = dest.split(TOKEN.POINT)
        return ImportStatementConfig(
            inner_val=inner_val,
            inner_attr=inner_attr,
            attr=attr,
            name=name,
            statement=f"from {inner_val}.{inner_attr}.{attr} import {name}",
        )

    @staticmethod
    def _get_rp_add_action(action: Dict[str, Any]) -> Optional[List[str]]:
        """Get replace and add action list from rules.

        :param action: Config migration module action.
        """

        def _build_import_statement(mod: str) -> str:
            spec = mod.rsplit(TOKEN.POINT, 1)
            return f"from {spec[0]} import {spec[1]}"

        if action is None:
            return []
        module = action[CONFIG.MODULE]
        if isinstance(module, str):
            return [_build_import_statement(module)]
        elif isinstance(module, list):
            return [_build_import_statement(mod) for mod in module]
        else:
            raise RuntimeError(
                "Invalid migration.module.action.module type: %s" % type(module)
            )

    def imp_migrator(self) -> Dict[str, ImportConfig]:
        """Get all import migrator from rules."""
        imps = {}

        for content in self._handle_rules_path(*self.imports_path):
            replace = self.get_module_action(
                content[CONFIG.MIGRATION], CONFIG.KW_REPLACE
            )
            add = self.get_module_action(content[CONFIG.MIGRATION], CONFIG.KW_ADD)
            remove = self.get_module_action(content[CONFIG.MIGRATION], CONFIG.KW_REMOVE)

            src = replace[CONFIG.SOURCE]
            if isinstance(src, str):
                imps[src] = ImportConfig(
                    replace=self._build_replace_importer(replace),
                    add=self._get_rp_add_action(add),
                    remove=self._get_rp_add_action(remove),
                )
            elif isinstance(src, list):
                for inner_src in src:
                    imps[inner_src] = ImportConfig(
                        replace=self._build_replace_importer(replace),
                        add=self._get_rp_add_action(add),
                        remove=self._get_rp_add_action(remove),
                    )

        return imps
