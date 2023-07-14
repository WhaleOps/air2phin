import logging
import warnings
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

from air2phin.constants import ConfigKey, Regexp, Token
from air2phin.core.rules.loader import rule_calls, rule_imports
from air2phin.utils.file import read_yaml, recurse_files

logger = logging.getLogger("air2phin.config")


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


class ImportConfig(NamedTuple):
    """Import config."""

    replace: str
    add: List[str]
    remove: bool


class Config:
    """Configurations of air2phin, including all configs change behavior of air2phin.

    :param customs: User custom path of rules, will combine with build-in rules when :param:``customs_only``
        is False, will only use custom rules and ignore build-in rules when :param:``customs_only`` is True.
    :param customs_only: Only use custom rules or not.
    :param inplace: Replace source python file inplace instead of create a new file.
    :param imports: Build-in imports rules path.
    :param calls: Build-in call rules path.
    """

    def __init__(
        self,
        customs: Optional[List[Path]] = None,
        customs_only: Optional[bool] = False,
        inplace: Optional[bool] = False,
        imports: Optional[List[Path]] = rule_imports,
        calls: Optional[List[Path]] = rule_calls,
    ):
        self._customs = customs
        self.customs_only = customs_only
        if self.customs_only and not self._customs:
            raise ValueError(
                "Argument `customs` not allow value None, when customs_only is True."
            )
        if self.customs_only:
            warnings.warn(
                "Will only use customs rules to migration, will ignore built-in rules.",
                UserWarning,
                stacklevel=2,
            )
        self.inplace = inplace
        self._imports = imports
        self._calls = calls
        # Want to be compatible with python 3.6 and python 3.7, so can not use
        # ``from functools import cached_property``
        self._call_migrator: Dict[str, CallConfig] | None = None
        self._import_migrator: Dict[str, ImportConfig] | None = None

    @property
    def imports_path(self) -> List[Path]:
        """Get all imports path for migration rules, the built-in rules before custom rules.

        Will only use :param:``customs`` rules and ignore built-in rules when :param:``customs_only`` is True,
        and combine :param:``customs``, built-in rules when :param:``customs_only`` is False.
        """
        if self.customs_only:
            return self._customs

        if not self._customs:
            return self._imports
        self._imports.extend(self._customs)
        return self._imports

    @property
    def imports(self) -> Dict[str, ImportConfig]:
        """Get all import migrator from rules."""
        if self._import_migrator:
            return self._import_migrator
        self._import_migrator = self.imp_migrator()
        return self._import_migrator

    @property
    def calls_path(self) -> List[Path]:
        """Get all call path for migration rules, the built-in rules before custom rules.

        Will only use :param:``customs`` rules and ignore built-in rules when :param:``customs_only`` is True,
        and combine :param:``customs``, built-in rules when :param:``customs_only`` is False.
        """
        if self.customs_only:
            return self._customs

        if not self._customs:
            return self._calls
        self._calls.extend(self._customs)
        return self._calls

    @property
    def calls(self) -> Dict[str, CallConfig]:
        """Get all call migrator from rules."""
        if self._call_migrator:
            return self._call_migrator
        self._call_migrator = self.call_migrator()
        return self._call_migrator

    @staticmethod
    def _build_caller(
        src: str, dest: str, parameters: List[Dict[str, Any]]
    ) -> CallConfig:
        replace = dict()
        add = dict()
        remove = []

        if parameters:
            for p in parameters:
                if p[ConfigKey.ACTION] == ConfigKey.KW_REPLACE:
                    replace[p[ConfigKey.SOURCE]] = p[ConfigKey.DESTINATION]
                elif p[ConfigKey.ACTION] == ConfigKey.KW_ADD:
                    add[p[ConfigKey.ARGUMENT]] = ParamDefaultConfig(
                        type=p[ConfigKey.DEFAULT][ConfigKey.TYPE],
                        value=p[ConfigKey.DEFAULT][ConfigKey.VALUE],
                    )
                elif p[ConfigKey.ACTION] == ConfigKey.KW_REMOVE:
                    remove.append(p[ConfigKey.ARGUMENT])
                else:
                    raise ValueError(
                        f"Unknown action type {p[ConfigKey.ACTION]} in {p}"
                    )

        return CallConfig(
            long=dest,
            short=dest.split(Token.POINT)[-1],
            src_long=src,
            src_short=src.split(Token.POINT)[-1],
            replace=replace,
            add=add,
            remove=remove,
        )

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
            for action in migration[ConfigKey.MODULE]
            if action[ConfigKey.ACTION] == action_type
        ]
        if len(actions) > 1:
            raise ValueError("Each type of action can only have one.")
        return actions[0] if actions else None

    @staticmethod
    def rules_override(rule_paths: List[Path]) -> List[Dict]:
        """Handle rules override, override the previous rules by the latest one when have the same name.

        Use dict comprehension to overwrite built-in rules, if custom rules also have the same name rules,
        will use the latest rules pass to :class:`Config`.
        """
        rules_map = {}

        rule_files = []
        for path in rule_paths:
            rule_files.extend(recurse_files(path, include=Regexp.PATH_YAML))

        for filename in rule_files:
            content = read_yaml(filename)
            rule_name = content.get(ConfigKey.NAME)
            if rule_name in rules_map:
                logger.info(
                    "Rule name with %s will be override by file %s", rule_name, filename
                )
            rules_map[rule_name] = content
        return list(rules_map.values())

    def call_migrator(self) -> Dict[str, CallConfig]:
        """Get all call migrator from rules."""
        migrator = {}

        for rule in self.rules_override(self.calls_path):
            migration = rule[ConfigKey.MIGRATION]
            parameters = migration.get(ConfigKey.PARAMETER, None)
            replace = self.get_module_action(migration, ConfigKey.KW_REPLACE)
            if replace is None:
                continue
            src = replace[ConfigKey.SOURCE]
            dest = replace[ConfigKey.DESTINATION]

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

    @staticmethod
    def _build_replace_importer(action: Dict[str, Any]) -> Optional[str]:
        if action is None:
            return None
        dest = action[ConfigKey.DESTINATION]
        module, asname = dest.rsplit(Token.POINT, 1)
        return f"from {module} import {asname}"

    @staticmethod
    def _get_rp_add_action(action: Dict[str, Any]) -> List[str]:
        """Get replace and add action list from rules.

        :param action: Config migration module action.
        """

        def _build_import_statement(mod: str) -> str:
            spec = mod.rsplit(Token.POINT, 1)
            return f"from {spec[0]} import {spec[1]}"

        if action is None:
            return []
        module = action[ConfigKey.MODULE]
        if isinstance(module, str):
            return [_build_import_statement(module)]
        elif isinstance(module, list):
            return [_build_import_statement(mod) for mod in module]
        else:
            raise RuntimeError(
                "Invalid migration.module.action.module type: %s" % type(module)
            )

    @staticmethod
    def _build_remove_importer(action: Dict[str, Any]) -> bool:
        if action is None or ConfigKey.MODULE not in action:
            return False
        return True

    def imp_migrator(self) -> Dict[str, ImportConfig]:
        """Get all import migrator from rules."""
        imps = {}

        for rule in self.rules_override(self.imports_path):
            replace = self.get_module_action(
                rule[ConfigKey.MIGRATION], ConfigKey.KW_REPLACE
            )
            add = self.get_module_action(rule[ConfigKey.MIGRATION], ConfigKey.KW_ADD)
            remove = self.get_module_action(
                rule[ConfigKey.MIGRATION], ConfigKey.KW_REMOVE
            )

            qualname = (
                replace[ConfigKey.SOURCE] if replace else remove[ConfigKey.MODULE]
            )
            if isinstance(qualname, str):
                imps[qualname] = ImportConfig(
                    replace=self._build_replace_importer(replace),
                    add=self._get_rp_add_action(add),
                    remove=self._build_remove_importer(remove),
                )
            elif isinstance(qualname, list):
                for inner_src in qualname:
                    imps[inner_src] = ImportConfig(
                        replace=self._build_replace_importer(replace),
                        add=self._get_rp_add_action(add),
                        remove=self._build_remove_importer(remove),
                    )

        return imps
