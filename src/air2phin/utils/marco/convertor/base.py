from __future__ import annotations

import logging
from typing import NamedTuple

log = logging.getLogger(__name__)


class DolphinHumanReadMarco(NamedTuple):
    marco: str
    # name is optional when can not convert to ds ones
    name: str | None = None


class BaseMacroConvertor:
    ds_base_date: str
    ds_marco_offset: str = None

    MACRO_FUNC_CONVERT = {
        "ds": "yyyy-MM-dd",
        "ds_nodash": "yyyyMMdd",
        "ts": "yyyy-MM-dd HH:mm:ss",
        "ts_nodash": "yyyyMMddHHmmss",
    }

    def __init__(self, macro_func: str):
        self.macro_func = macro_func

    def parse_ds_base_date(self) -> None:
        self.ds_base_date = self.MACRO_FUNC_CONVERT.get(self.macro_func)
        if self.ds_base_date is None:
            log.info(f"get unexpect macro func {self.macro_func}")

    def parse_ds_offset(self) -> None:
        pass

    def get_human_read_name(self) -> str:
        return self.macro_func

    def get_source_airflow_marco(self) -> str:
        return f"{{{{ {self.macro_func} }}}}"

    def get_ds_marco(self) -> DolphinHumanReadMarco | None:
        self.parse_ds_base_date()
        self.parse_ds_offset()
        if self.ds_base_date is None:
            return DolphinHumanReadMarco(marco=self.get_source_airflow_marco())
        if self.ds_marco_offset is None:
            if self.ds_base_date is None:
                return None
            return DolphinHumanReadMarco(
                name=self.get_human_read_name(), marco=f"$[{self.ds_base_date}]"
            )
        else:
            return DolphinHumanReadMarco(
                name=self.get_human_read_name(),
                marco=f"$[{self.ds_base_date}{self.ds_marco_offset}]",
            )
