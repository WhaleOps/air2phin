from typing import Optional

from air2phin.fake.core.connection import Connection
from air2phin.fake.core.hook import BaseHook


class MySqlHook(BaseHook):
    """Interact with MySQL.

    This hook is a fake hook for Airflow MySQL hook, to allow user do not change their code but use
    dolphinscheduler datasource connection to connect to MySQL database.

    :param connection: specific hook connection. :class:``air2phin.fake.core.connection.Connection`` object.
    """

    def __init__(
        self,
        conn_name_attr: Optional[str] = None,
        connection: Optional[Connection] = None,
        *args,
        **kwargs
    ):
        super().__init__(conn_name_attr, connection)

    def get_conn(self) -> "MySQLdb.connections.Connection":  # noqa: F821
        """Get MySQL connection object."""
        try:
            import MySQLdb
        except ImportError:
            raise ImportError("This MySQLdb module does not seem to be installed.")

        connection = super().get_conn()
        conn_args = dict(
            host=connection.host,
            port=connection.port,
            db=connection.schema,
            user=connection.login,
            passwd=connection.password,
        )
        return MySQLdb.connect(**conn_args)
