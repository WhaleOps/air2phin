from __future__ import annotations

import json
import os
import re
from contextlib import closing
from typing import Any, Callable, Iterable, Mapping, Optional, Tuple, Union

import sqlparse
from sqlalchemy import create_engine, text

from air2phin.constants import Token
from air2phin.fake.core.connection import Connection


def fetch_all_handler(cursor) -> list[tuple] | None:
    """Handler for DbApiHook.run() to return results."""
    if cursor.description is not None:
        return cursor.fetchall()
    else:
        return None


class BaseHook:
    """Base hook for all fake hook.

    This hook is a fake hook for Airflow base hook, to allow user do not change their code but use
    dolphinscheduler datasource connection to connect specific datasource.

    :param connection: specific hook connection. :class:``air2phin.fake.core.connection.Connection`` object.
    """

    def __init__(
        self,
        conn_name_attr: Optional[str] = None,
        connection: Optional[Connection] = None,
    ):
        self.conn_name_attr = conn_name_attr
        self.connection = connection

    def get_conn(self):
        """Get hook connection object, depend on subclass return type."""
        if self.connection:
            return self.connection
        elif self.conn_name_attr:
            self.connection = self.get_connection(self.conn_name_attr)
            return self.connection
        else:
            raise ValueError(
                "Can not get connection, nether parameter ``conn_name_attr``"
                "nor ``connection`` provided."
            )

    @staticmethod
    def parser_conn_namedtuple(connection_params: str) -> Connection:
        """Parse dolphinscheduler connection_params to Connection.

        :param connection_params: connection_params from dolphinscheduler datasource.
        """
        data = json.loads(connection_params)

        pattern = re.compile(
            "jdbc:.*://(?P<host>[\\w\\W]+):(?P<port>\\d+)/(?P<database>\\w+)(\\?|$)"
        )
        # node name change to url when using seatunnel datasource connector
        try:
            pattern_match = pattern.match(
                data.get("jdbcUrl", data.get("url", None))
            ).groupdict()
        except Exception:
            raise ValueError(
                f"Can not parser connection params, make sure connection in format "
                f"`jdbc:dbtype://host:port/database` which is only acceptable by air2phin, "
                f"currently is : {connection_params}"
            )

        return Connection(
            host=pattern_match.get("host", None),
            port=int(pattern_match.get("port", None)),
            schema=pattern_match.get("database", None),
            login=data.get("user", None),
            password=data.get("password", None),
        )

    @staticmethod
    def _get_type_name(conn_id) -> Tuple[Any, str]:
        if Token.POINT in conn_id:
            return conn_id.strip().split(Token.POINT)
        return None, conn_id.strip()

    @classmethod
    def _get_connection_params_from_env(
        cls, metadata_conn: str, conn_id: str
    ) -> Connection:
        sql_qry_type_name = (
            "SELECT connection_params FROM t_ds_datasource WHERE type = {type} and "
            "name = '{name}'"
        )
        sql_qry_name = (
            "SELECT connection_params FROM t_ds_datasource WHERE name = '{name}'"
        )

        database_type_map = dict(
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

        datasource_type, datasource_name = cls._get_type_name(conn_id)
        engine = create_engine(metadata_conn, echo=True)

        with engine.connect() as conn:
            # conn_id not in format of datasource_type.datasource_name
            if Token.POINT not in conn_id:
                result_name = conn.execute(
                    text(sql_qry_name.format(name=datasource_name))
                )
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
            if datasource_type.lower() not in database_type_map:
                raise ValueError(
                    f"Datasource type `{datasource_type}` not support currently, please use one of "
                    f"{list(database_type_map.keys())}"
                )
            result_type_name = conn.execute(
                text(
                    sql_qry_type_name.format(
                        type=database_type_map.get(datasource_type),
                        name=datasource_name,
                    )
                )
            )
            if result_type_name.rowcount == 0:
                raise ValueError(
                    f"Connection {conn_id} not found in dolphinscheduler metadata database."
                )
            record = result_type_name.fetchone()
            return cls.parser_conn_namedtuple(record[0])

    @classmethod
    def get_connection(cls, conn_id: str) -> Connection:
        """Get connection from dolphinscheduler metadata database.

        This method is a fake function for Airflow connection get_connection, to allow user do not change
        their code but use dolphinscheduler datasource and return
        :class:``air2phin.fake.core.connection.Connection`` object.

        :param conn_id: connection id, if in format of datasource_type.datasource_name, will query by type
            and name, and if only use datasource_name, will query by name only.
        """
        try:
            from pydolphinscheduler.models.datasource import Datasource

            datasource_type, datasource_name = cls._get_type_name(conn_id)
            database: Datasource = Datasource.get(
                datasource_name=datasource_name, datasource_type=datasource_type
            )
            return cls.parser_conn_namedtuple(database.connection_params)
        except ImportError:
            metadata_conn = os.environ.get("AIR2PHIN_FAKE_CONNECTION", None)
            if metadata_conn is None:
                raise ValueError(
                    "Can not get dolphinscheduler metadata connection information, neither package"
                    "``pydolphinscheduler`` installed nor environment variable ``AIR2PHIN_FAKE_CONNECTION``"
                    "is set, please do one of them to keep going."
                )
            return cls._get_connection_params_from_env(metadata_conn, conn_id)

    def _run_command(self, cur, sql_statement, parameters):
        """Execute command."""
        if parameters:
            cur.execute(sql_statement, parameters)
        else:
            cur.execute(sql_statement)

    def run(
        self,
        sql: Union[str, Iterable[str]],
        autocommit: bool = False,
        parameters: Union[Iterable, Mapping, None] = None,
        handler: Union[Callable, None] = None,
        split_statements: bool = False,
        return_last: bool = True,
    ) -> Union[Any, list[Any], None]:
        """Mock sql run command."""
        scalar_return_last = isinstance(sql, str) and return_last
        if isinstance(sql, str):
            if split_statements:
                splits = sqlparse.split(sqlparse.format(sql, strip_comments=True))
                sql: list[str] = list(filter(None, splits))
            else:
                sql = [sql]

        if not sql:
            raise ValueError("List of SQL statements is empty")

        with closing(self.get_conn()) as conn:
            with closing(conn.cursor()) as cur:
                results = []
                for sql_statement in sql:
                    self._run_command(cur, sql_statement, parameters)

                    if handler is not None:
                        result = handler(cur)
                        results.append(result)

            if autocommit:
                conn.commit()

        if handler is None:
            return None
        elif scalar_return_last:
            return results[-1]
        else:
            return results

    @staticmethod
    def fetch_all_handler(cursor) -> Union[list[tuple], None]:
        """Handler for DbApiHook.run() to return results."""
        if cursor.description is not None:
            return cursor.fetchall()
        else:
            return None

    def get_records(
        self,
        sql: Union[str, list[str]],
        parameters: Union[Iterable, Mapping, None] = None,
    ) -> Any:
        """Mock executes sql and returns records."""
        return self.run(sql=sql, parameters=parameters, handler=fetch_all_handler)
