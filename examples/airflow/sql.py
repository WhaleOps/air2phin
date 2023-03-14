from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator


def print_context(ds, **kwargs):
    print(ds)


with DAG(
    "sql",
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2021, 1, 1),
) as dag:
    run_this = PostgresOperator(
        task_id="sql",
        postgres_conn_id="meta",
        sql="./test.sql",
    )
