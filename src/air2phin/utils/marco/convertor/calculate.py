from __future__ import annotations

import logging
from datetime import timedelta

from air2phin.utils.marco.convertor.base import BaseMacroConvertor
from air2phin.utils.reshape import day2unit_convert, timedelta2structure

log = logging.getLogger(__name__)


class CalculateMacroConvertor(BaseMacroConvertor):
    MACRO_FUNC_CONVERT = {
        "ts_tz_add": "yyyy-MM-dd HH:mm:ss",
        "dt_tz_add": "yyyy-MM-dd",
        "ts_tz_add_ms": "yyyy-MM-dd HH:mm:ss",
        "dt_tz_add_ms": "yyyy-MM-dd",
    }
    DEFAULT_OFFSET = timedelta(seconds=0)

    def __init__(
        self,
        macro_func: str,
        base_date: str,
        offset_unit: str | None,
        offset_num: int | None,
        schedule: timedelta | None = None,
    ):
        super().__init__(macro_func)
        self.base_date = base_date
        self.offset_unit = offset_unit
        self.offset_num = offset_num
        self.schedule = schedule

    def get_source_airflow_marco(self) -> str:
        if self.offset_unit is None or self.offset_num is None:
            return f"{{{{ {self.macro_func}({self.base_date}) }}}}"
        return f"{{{{ {self.macro_func}({self.base_date}, {self.offset_unit}={self.offset_num}) }}}}"

    def get_human_read_name(self) -> str:
        if self.base_date == "execution_date":
            if self.macro_func == "ts_tz_add":
                base = "datetime"
            elif self.macro_func == "dt_tz_add":
                base = "date"
            elif self.macro_func == "dt_tz_add_ms":
                base = "date_timestamp"
            elif self.macro_func == "ts_tz_add_ms":
                base = "datetime_timestamp"
        elif self.base_date == "next_execution_date":
            if self.macro_func == "ts_tz_add":
                base = "next_datetime"
            elif self.macro_func == "dt_tz_add":
                base = "next_date"
            elif self.macro_func == "dt_tz_add_ms":
                base = "next_date_timestamp"
            elif self.macro_func == "ts_tz_add_ms":
                base = "next_datetime_timestamp"
        else:
            raise ValueError(f"get unexpect base date {self.base_date}")
        if self.offset_unit is None or self.offset_num is None:
            return base
        op = "add" if self.offset_num > 0 else "sub"
        offset = f"{abs(self.offset_num)}{self.offset_unit}"
        return f"{base}_{op}_{offset}"

    def get_ds_marco_offset(self) -> str:
        base_date_convert = {
            "execution_date": self.DEFAULT_OFFSET,
            "next_execution_date": self.schedule,
        }

        # hint
        if self.offset_unit is not None and self.offset_unit not in day2unit_convert:
            log.warning(f"get unexpect offset unit {self.offset_unit}")
        if self.base_date not in base_date_convert:
            log.warning(f"get unexpect macro func {self.base_date}")

        # parse offset
        offset = base_date_convert.get(self.base_date, self.DEFAULT_OFFSET)
        if self.offset_unit is not None:
            offset += timedelta(**{self.offset_unit: self.offset_num})

        structure_timedelta = timedelta2structure(offset)
        if offset.total_seconds() > 0:
            return f"+{structure_timedelta.ds_offset()}"
        else:
            return f"-{structure_timedelta.ds_offset()}"

    def parse_ds_offset(self) -> None:
        base_date_convert = {
            "execution_date": self.DEFAULT_OFFSET,
            "next_execution_date": self.schedule,
        }

        # hint
        if self.offset_unit is not None and self.offset_unit not in day2unit_convert:
            log.warning(f"get unexpect offset unit {self.offset_unit}")
        if self.base_date not in base_date_convert:
            log.warning(f"get unexpect macro func {self.base_date}")

        # parse offset
        offset = base_date_convert.get(self.base_date, self.DEFAULT_OFFSET)
        if self.offset_unit is not None:
            offset += timedelta(**{self.offset_unit: self.offset_num})

        structure_timedelta = timedelta2structure(offset)
        if offset.total_seconds() > 0:
            self.ds_marco_offset = f"+{structure_timedelta.ds_offset()}"
        else:
            self.ds_marco_offset = f"-{structure_timedelta.ds_offset()}"
