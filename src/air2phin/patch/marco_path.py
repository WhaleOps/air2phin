from __future__ import annotations

from datetime import timedelta

from pydolphinscheduler.core import Workflow

from air2phin.utils.marco import helper
from air2phin.utils.marco.convertor.base import DolphinHumanReadMarco
from air2phin.utils.reshape import schedule2timedelta


class PatchMarco:
    def __init__(
        self,
        workflow: Workflow,
    ):
        self.workflow = workflow

    def patch(self) -> None:
        schedule: str | timedelta = self.workflow.schedule
        td: timedelta = schedule2timedelta(schedule)

        marcos: set[DolphinHumanReadMarco] = set()
        for task_name, task in self.workflow.tasks.items():
            if task.ext_attr is not None:
                render_field = task.ext_attr.lstrip("_")
                srv_val = getattr(task, render_field)
                if not isinstance(srv_val, str | bytes):
                    continue
                task_define_marco = helper.replace_marco(srv_val, td)
                setattr(task, render_field, task_define_marco.content)

                if task_define_marco.marco is not None:
                    marcos |= task_define_marco.marco

        if marcos:
            self.workflow.param = {marco.name: marco.marco for marco in marcos}
