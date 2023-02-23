from air2phin.fake.core.connection import Connection
from air2phin.fake.core.hook import BaseHook

try:
    import psycopg2
except ImportError:
    raise ImportError("This psycopg2 module does not seem to be installed.")


class PostgresHook(BaseHook):
    """Interact with PostgresSQL.

    This hook is a fake hook for Airflow Postgres hook, to allow user do not change their code but use
    dolphinscheduler datasource connection to connect to PostgresSQL database.

    :param connection: specific hook connection. :class:``air2phin.fake.core.connection.Connection`` object.
    """

    def __init__(self, connection: Connection, *args, **kwargs):
        super().__init__(connection)

    def get_conn(self) -> "psycopg2.extensions.connection":
        """Get postgres connection object."""
        conn_args = dict(
            host=self.connection.host,
            port=self.connection.port,
            dbname=self.connection.schema,
            user=self.connection.login,
            password=self.connection.password,
        )
        return psycopg2.connect(**conn_args)
