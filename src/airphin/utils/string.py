from airphin.constants import KEYWORD, NUMBER, TOKEN


def convert_schedule(val: str) -> str:
    """Convert airflow schedule string to dolphinscheduler's.

    Will convert including:
    * crontab schedule string from ``5 4 * * *`` to ```0 5 4 * * ? *``
    * shortcut schedule string like ``@daily`` to ``0 0 0 * * ? *``.
    """
    if (
        len(val) == NUMBER.SCHEDULE_TOTAL_NUM
        and val.count(TOKEN.SPACE) == NUMBER.SCHEDULE_SPACE_NUM
    ):
        val_list = val.split(TOKEN.SPACE)
        val_list.insert(0, TOKEN.ZERO)
        val_list.insert(-1, TOKEN.QUESTION)
        return TOKEN.SPACE.join(val_list)
    return KEYWORD.DEFAULT_SCHEDULE
