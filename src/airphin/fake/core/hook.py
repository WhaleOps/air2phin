import json
import os
import re

from sqlalchemy import create_engine, text

from airphin.constants import TOKEN
from airphin.fake.core.connection import Connection


class BaseHook:
    """Base hook for all fake hook.

    This hook is a fake hook for Airflow base hook, to allow user do not change their code but use
    dolphinscheduler datasource connection to connect specific datasource.

    :param connection: specific hook connection. :class:``airphin.fake.core.connection.Connection`` object.
    """

    query_type_name = (
        "SELECT connection_params FROM t_ds_datasource WHERE type = '{type}' "
        "and name = '{name}'"
    )
    query_name = "SELECT connection_params FROM t_ds_datasource WHERE name = '{name}'"
    pattern = re.compile("jdbc:.*://(?P<host>[\\w\\W]+):(?P<port>\\d+)")

    def __init__(self, connection: Connection):
        self.connection = connection

    def get_conn(self):
        """Get hook connection object, depend on subclass return type."""
        raise NotImplementedError

    @classmethod
    def parser_conn_namedtuple(cls, connection_params: str) -> Connection:
        """Parse dolphinscheduler connection_params to Connection.

        :param connection_params: connection_params from dolphinscheduler datasource.
        """
        data = json.loads(connection_params)

        address_match = cls.pattern.match(data.get("jdbcUrl", None)).groupdict()

        return Connection(
            host=address_match.get("host", None),
            port=int(address_match.get("port", None)),
            schema=data.get("database", None),
            login=data.get("user", None),
            password=data.get("password", None),
        )

    @classmethod
    def get_connection(cls, conn_id: str) -> Connection:
        """Get connection from dolphinscheduler metadata database.

        This method is a fake function for Airflow connection get_connection, to allow user do not change
        their code but use dolphinscheduler datasource and return
        :class:``airphin.fake.core.connection.Connection`` object.

        :param conn_id: connection id, if in format of datasource_type.datasource_name, will query by type
            and name, and if only use datasource_name, will query by name only.
        """
        ds_metadata = os.environ.get("AIRPHIN_FAKE_CONNECTION", None)
        if ds_metadata is None:
            raise ValueError(
                "AIRPHIN_FAKE_CONNECTION is not set in environment variables"
            )

        engine = create_engine(ds_metadata, echo=True)

        with engine.connect() as conn:
            # conn_id not in format of datasource_type.datasource_name
            if TOKEN.POINT not in conn_id:
                result_name = conn.execute(text(cls.query_name.format(name=conn_id)))
                if result_name.rowcount == 0:
                    raise ValueError(
                        f"Connection {conn_id} not found in dolphinscheduler metadata database."
                    )
                elif result_name.rowcount > 1:
                    raise ValueError(
                        f"Connection {conn_id} is not unique in dolphinscheduler metadata database, please "
                        f"use ``datasource_type.datasource_name`` to specify."
                    )
                record = result_name.fetchone()
                return cls.parser_conn_namedtuple(record[0])

            # conn_id in format of datasource_type.datasource_name
            dst, dsn = conn_id.split(TOKEN.POINT)
            result_type_name = conn.execute(
                text(cls.query_name.format(type=dst, name=dsn))
            )
            if result_type_name.rowcount == 0:
                raise ValueError(
                    f"Connection {conn_id} not found in dolphinscheduler metadata database."
                )
            record = result_type_name.fetchone()
            return cls.parser_conn_namedtuple(record[0])
