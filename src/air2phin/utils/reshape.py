from __future__ import annotations

from datetime import datetime, timedelta
from typing import NamedTuple

import croniter

SEC_2_MIN = 60
SEC_2_HOUR = SEC_2_MIN * 60
SEC_2_DAY = SEC_2_HOUR * 24

# unit: [day2unit, unit2day_ds_marco]
day2unit_convert = {
    "days": "",
    "hours": "/24",
    "minutes": "/60/24",
    "seconds": "/60/60/24",
}


class StructureTimedelta(NamedTuple):
    unit: str
    value: int
    convert: str

    def ds_offset(self) -> str:
        return f"{self.value}{self.convert}" if self.convert != "" else f"{self.value}"


def timedelta2structure(td: timedelta) -> StructureTimedelta:
    total_seconds = abs(int(td.total_seconds()))
    minutes, remainder = divmod(total_seconds, SEC_2_MIN)
    if remainder > 0:
        return StructureTimedelta(
            unit="seconds", value=total_seconds, convert=day2unit_convert.get("seconds")
        )
    hours, remainder = divmod(total_seconds, SEC_2_HOUR)
    if remainder > 0:
        return StructureTimedelta(
            unit="minutes", value=minutes, convert=day2unit_convert.get("minutes")
        )
    days, remainder = divmod(total_seconds, SEC_2_DAY)
    if remainder > 0:
        return StructureTimedelta(
            unit="hours", value=hours, convert=day2unit_convert.get("hours")
        )
    else:
        return StructureTimedelta(
            unit="days", value=days, convert=day2unit_convert.get("days")
        )


def schedule2timedelta(schedule: str | timedelta) -> timedelta:
    if isinstance(schedule, timedelta):
        return schedule
    if schedule.startswith("@"):
        raise NotImplementedError("Airflow shortcut schedule not support, currently")

    now = datetime.now()
    cron = croniter.croniter(schedule, now)
    post = cron.get_next(datetime)
    post_plus = cron.get_next(datetime)
    return post_plus - post
