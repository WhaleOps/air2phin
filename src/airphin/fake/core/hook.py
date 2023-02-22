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

    _QUERY_TYPE_NAME = (
        "SELECT connection_params FROM t_ds_datasource WHERE type = {type} "
        "and name = '{name}'"
    )
    _QUERY_NAME = "SELECT connection_params FROM t_ds_datasource WHERE name = '{name}'"
    _PATTERN = re.compile("jdbc:.*://(?P<host>[\\w\\W]+):(?P<port>\\d+)")

    _DATABASE_TYPE_MAP = dict(
        mysql=0,
        postgresql=1,
        hive=2,
        spark=3,
        clickhouse=4,
        oracle=5,
        sqlserver=6,
        db2=7,
        presto=8,
        h2=9,
        redshift=10,
        dameng=11,
        starrocks=12,
    )

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

        address_match = cls._PATTERN.match(data.get("jdbcUrl", None)).groupdict()

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
                result_name = conn.execute(text(cls._QUERY_NAME.format(name=conn_id)))
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
            dst, dsn = conn_id.strip().split(TOKEN.POINT)
            if dst.lower() not in cls._DATABASE_TYPE_MAP:
                raise ValueError(
                    f"Datasource type `{dst}` not support currently, please use one of "
                    f"{list(cls._DATABASE_TYPE_MAP.keys())}"
                )
            result_type_name = conn.execute(
                text(cls._QUERY_NAME.format(type=dst, name=dsn))
            )
            if result_type_name.rowcount == 0:
                raise ValueError(
                    f"Connection {conn_id} not found in dolphinscheduler metadata database."
                )
            record = result_type_name.fetchone()
            return cls.parser_conn_namedtuple(record[0])
