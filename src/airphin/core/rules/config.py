from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

from airphin.constants import CONFIG, REGEXP, TOKEN
from airphin.core.rules.loader import rule_calls, rule_imports
from airphin.utils.file import read_multi_yaml, read_yaml


class CallConfig(NamedTuple):
    """Call statement config."""

    long: str
    short: str
    param: Dict[str, Any]
    default: Dict[str, Any]
    src_long: str
    src_short: str


class ImportConfig(NamedTuple):
    """Import statement config."""

    inner_val: str
    inner_attr: str
    attr: str
    name: str
    statement: str


class Config:
    """Configurations of airphin, including all configs change behavior of airphin.

    :param customs: User custom path of rules, can overwrite build-in rules.
    :param imports: Build-in imports rules path.
    :param calls: Build-in call rules path.
    """

    def __init__(
        self,
        customs: Optional[List[Path]] = None,
        imports: Optional[List[Path]] = rule_imports,
        calls: Optional[List[Path]] = rule_calls,
    ):
        self._customs = customs
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
        """Get all import convertor from rules."""
        return self.imp_convertor()

    @property
    def calls_path(self) -> List[Path]:
        """Get all call rules path."""
        if not self._customs:
            return self._calls
        self._calls.extend(self._customs)
        return self._calls

    @property
    def calls(self) -> Dict[str, CallConfig]:
        """Get all call convertor from rules."""
        return self.call_convertor()

    @staticmethod
    def _build_caller(src, migrate: Dict[str, Any]) -> CallConfig:
        dest = migrate[CONFIG.MODULE][CONFIG.DESTINATION]
        return CallConfig(
            long=dest,
            short=dest.split(TOKEN.POINT)[-1],
            param={
                p[CONFIG.SOURCE]: p[CONFIG.DESTINATION]
                for p in migrate[CONFIG.PARAMETER]
            },
            default={
                p[CONFIG.DESTINATION]: p[CONFIG.DEFAULT]
                for p in migrate[CONFIG.PARAMETER]
                if CONFIG.DEFAULT in p
            },
            src_long=src,
            src_short=src.split(TOKEN.POINT)[-1],
        )

    @staticmethod
    def _build_importer(migrate: Dict[str, Any]) -> ImportConfig:
        dest = migrate[CONFIG.MODULE][CONFIG.DESTINATION]
        inner_val, inner_attr, attr, name = dest.split(TOKEN.POINT)
        return ImportConfig(
            inner_val=inner_val,
            inner_attr=inner_attr,
            attr=attr,
            name=name,
            statement=f"from {inner_val}.{inner_attr}.{attr} import {name}",
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

    def call_convertor(self) -> Dict[str, CallConfig]:
        """Get all call convertor from rules."""
        convertor = {}

        for content in self._handle_rules_path(*self.calls_path):
            migration = content[CONFIG.MIGRATION]
            src = migration[CONFIG.MODULE][CONFIG.SOURCE]
            if isinstance(src, str):
                convertor[src] = self._build_caller(src, migration)
            elif isinstance(src, list):
                for inner_src in src:
                    convertor[inner_src] = self._build_caller(inner_src, migration)
            else:
                raise RuntimeError("Invalid migration.module.src type: %s" % type(src))
        return convertor

    def imp_convertor(self) -> Dict[str, ImportConfig]:
        """Get all import convertor from rules."""
        convertor = {}

        for content in self._handle_rules_path(*self.imports_path):
            migration = content[CONFIG.MIGRATION]
            src = migration[CONFIG.MODULE][CONFIG.SOURCE]
            if isinstance(src, str):
                convertor[src] = self._build_importer(migration)
            elif isinstance(src, list):
                for inner_src in src:
                    convertor[inner_src] = self._build_importer(migration)
            else:
                raise RuntimeError("Invalid migration.module.src type: %s" % type(src))
        return convertor
