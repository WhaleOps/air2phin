from air2phin.constants import Keyword, Number, Token


def convert_schedule(val: str) -> str:
    """Convert airflow schedule string to dolphinscheduler's.

    Will convert including:
    * crontab schedule string from ``5 4 * * *`` to ```0 5 4 * * ? *``
    * shortcut schedule string like ``@daily`` to ``0 0 0 * * ? *``.
    """
    if (
        len(val) == Number.SCHEDULE_TOTAL_NUM
        and val.count(Token.SPACE) == Number.SCHEDULE_SPACE_NUM
    ):
        val_list = val.split(Token.SPACE)
        val_list.insert(0, Token.ZERO)
        val_list.insert(-1, Token.QUESTION)
        return Token.SPACE.join(val_list)
    return Keyword.DEFAULT_SCHEDULE
