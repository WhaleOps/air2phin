from typing import Optional

from air2phin.fake.core.connection import Connection
from air2phin.fake.core.hook import BaseHook


class PostgresHook(BaseHook):
    """Interact with PostgresSQL.

    This hook is a fake hook for Airflow Postgres hook, to allow user do not change their code but use
    dolphinscheduler datasource connection to connect to PostgresSQL database.

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

    def get_conn(self) -> "psycopg2.extensions.connection":  # noqa: F821
        """Get postgres connection object."""
        try:
            import psycopg2
        except ImportError:
            raise ImportError("This psycopg2 module does not seem to be installed.")

        connection = super().get_conn()
        conn_args = dict(
            host=connection.host,
            port=connection.port,
            dbname=connection.schema,
            user=connection.login,
            password=connection.password,
        )
        return psycopg2.connect(**conn_args)
