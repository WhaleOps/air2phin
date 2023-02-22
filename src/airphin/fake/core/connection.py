from typing import NamedTuple


class Connection(NamedTuple):
    """Connection Info store in dolphinscheduler metadata database."""

    host: str
    port: int
    schema: str
    login: str
    password: str
