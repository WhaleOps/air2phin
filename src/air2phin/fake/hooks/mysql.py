from air2phin.fake.core.connection import Connection
from air2phin.fake.core.hook import BaseHook


class MySqlHook(BaseHook):
    """Interact with MySQL.

    This hook is a fake hook for Airflow MySQL hook, to allow user do not change their code but use
    dolphinscheduler datasource connection to connect to MySQL database.

    :param connection: specific hook connection. :class:``air2phin.fake.core.connection.Connection`` object.
    """

    def __init__(self, connection: Connection, *args, **kwargs):
        super().__init__(connection)

    def get_conn(self) -> "MySQLdb.connections.Connection":  # noqa: F821
        """Get MySQL connection object."""
        try:
            import MySQLdb
        except ImportError:
            raise ImportError("This MySQLdb module does not seem to be installed.")

        conn_args = dict(
            host=self.connection.host,
            port=self.connection.port,
            db=self.connection.schema,
            user=self.connection.login,
            passwd=self.connection.password,
        )
        return MySQLdb.connect(**conn_args)
