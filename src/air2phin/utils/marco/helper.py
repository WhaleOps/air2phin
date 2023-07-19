from __future__ import annotations

import logging
import re
from datetime import timedelta
from pathlib import Path
from typing import NamedTuple

from air2phin.utils.marco.convertor.base import (
    BaseMacroConvertor,
    DolphinHumanReadMarco,
)
from air2phin.utils.marco.convertor.calculate import CalculateMacroConvertor
from air2phin.utils.string import escape_marco_bracket

log = logging.getLogger(__name__)


pattern_amarco = re.compile(r"\{\{ *(.+?) *\}\}")
pattern_unit = re.compile(
    r"(?P<macro_func>\w+)\((?P<base_date>\w+),\s*(?P<offset_unit>\w+)=(?P<offset_num>.*?)\)"
)
pattern_no_unit = re.compile(r"(?P<macro_func>\w+)\((?P<base_date>\w+)\)")


class AirflowMarco:
    def __init__(
        self,
        macro: str,
        schedule: timedelta | None,
    ):
        self.macro = macro
        self.schedule = schedule

    def parse2marco(self) -> BaseMacroConvertor | CalculateMacroConvertor | None:
        if "(" not in self.macro:
            return BaseMacroConvertor(macro_func=self.macro)
        if "," in self.macro:
            match = pattern_unit.match(self.macro)
            if match is None:
                log.warning(
                    f"get unexpect macro func {self.macro} and can not parse it"
                )
                return
            return CalculateMacroConvertor(
                macro_func=match.group("macro_func"),
                base_date=match.group("base_date"),
                offset_unit=match.group("offset_unit"),
                offset_num=int(match.group("offset_num")),
                schedule=self.schedule,
            )

        match = pattern_no_unit.match(self.macro)
        if match is None:
            log.warning(f"get unexpect macro func {self.macro} and can not parse it")
            return
        return CalculateMacroConvertor(
            macro_func=match.group("macro_func"),
            base_date=match.group("base_date"),
            offset_unit=None,
            offset_num=0,
            schedule=self.schedule,
        )


class TaskContentWithMarco(NamedTuple):
    content: str
    marco: set[DolphinHumanReadMarco] | None = None


def get_path_all_macros(path_str: str) -> set[str]:
    all_marco = set()
    path = Path(path_str)
    for p in path.glob("**/*"):
        if p.is_dir():
            continue
        with p.open() as f:
            content = f.read()
            find_lst = pattern_amarco.findall(content)
            if find_lst:
                all_marco.update((find.strip() for find in find_lst))
    return all_marco


def parse2ds_marco(
    amarco: str,
    schedule: timedelta | None,
) -> DolphinHumanReadMarco | None:
    airflow_marco = AirflowMarco(amarco, schedule)
    marco: CalculateMacroConvertor = airflow_marco.parse2marco()
    if marco is None:
        log.warning("parse marco `%s` failed", amarco)
        return None
    else:
        return marco.get_ds_marco()


def replace_marco(content: str, schedule: timedelta | None) -> TaskContentWithMarco:
    find_lst = pattern_amarco.findall(content)
    if not find_lst:
        return TaskContentWithMarco(content=content)

    marcos = set()
    for find in find_lst:
        if find is None:
            continue
        trim_key = find.strip()
        ds_marco: DolphinHumanReadMarco | None = parse2ds_marco(trim_key, schedule)
        if ds_marco is None or ds_marco.name is None:
            continue
        pattern = "'\\{\\{ *" + escape_marco_bracket(trim_key) + " *\\}\\}'"

        if "_timestamp" in ds_marco.name:
            new_ds_marco = "unix_timestamp('${" + ds_marco.name + "}')*1000"
        else:
            new_ds_marco = "'${" + ds_marco.name + "}'"
        content = re.compile(pattern).sub(new_ds_marco, content)
        marcos.add(ds_marco)
    return TaskContentWithMarco(
        content=content,
        marco=marcos,
    )
