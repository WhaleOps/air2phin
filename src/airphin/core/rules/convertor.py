from typing import Any, Dict, List, NamedTuple

from airphin.constants import REGEXP
from airphin.core.rules.loader import path_dag_cnx, path_operators
from airphin.utils.file import read_multi_yaml, read_yaml


class CallConverter(NamedTuple):
    long: str
    short: str
    param: Dict[str, Any]
    default: Dict[str, Any]
    src_long: str
    src_short: str


class ImportConverter(NamedTuple):
    inner_val: str
    inner_attr: str
    attr: str
    name: str
    statement: str


def _build_caller(src, migrate: Dict[str, Any]) -> CallConverter:
    dest = migrate["module"]["dest"]
    return CallConverter(
        long=dest,
        short=dest.split(".")[-1],
        param={p["src"]: p["dest"] for p in migrate["parameter"]},
        default={
            p["dest"]: p["default"] for p in migrate["parameter"] if "default" in p
        },
        src_long=src,
        src_short=src.split(".")[-1],
    )


def _build_importer(migrate: Dict[str, Any]) -> ImportConverter:
    dest = migrate["module"]["dest"]
    inner_val, inner_attr, attr, name = dest.split(".")
    return ImportConverter(
        inner_val=inner_val,
        inner_attr=inner_attr,
        attr=attr,
        name=name,
        statement=f"from {inner_val}.{inner_attr}.{attr} import {name}",
    )


def _handle_rules_path(*args) -> List[Dict[str, Any]]:
    for arg in args:
        if arg.is_file():
            content: Dict = read_yaml(arg)
            yield content
        if arg.is_dir():
            contents: List[Dict] = read_multi_yaml(arg.glob(REGEXP.PATH_YAML))
            for content in contents:
                yield content


def call_convertor(*args) -> dict[str, CallConverter]:
    convertor = {}

    for content in _handle_rules_path(*args):
        migration = content["migration"]
        src = migration["module"]["src"]
        if isinstance(src, str):
            convertor[src] = _build_caller(src, migration)
        elif isinstance(src, list):
            for inner_src in src:
                convertor[inner_src] = _build_caller(inner_src, migration)
        else:
            raise RuntimeError("Invalid migration.module.src type: %s" % type(src))
    return convertor


def imp_convertor(*args) -> dict[str, ImportConverter]:
    convertor = {}

    for content in _handle_rules_path(*args):
        migration = content["migration"]
        src = migration["module"]["src"]
        if isinstance(src, str):
            convertor[src] = _build_importer(migration)
        elif isinstance(src, list):
            for inner_src in src:
                convertor[inner_src] = _build_importer(migration)
        else:
            raise RuntimeError("Invalid migration.module.src type: %s" % type(src))
    return convertor


rule_import = [path_operators, path_dag_cnx]

rule_call = [
    path_operators,
    path_dag_cnx,
]


call_cov = call_convertor(*rule_call)
imp_cov = imp_convertor(*rule_import)
