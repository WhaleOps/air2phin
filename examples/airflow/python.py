from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator


def print_context(ds, **kwargs):
    print(ds)


with DAG(
    "tutorial",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
) as dag:
    run_this = PythonOperator(
        task_id="print_the_context",
        python_callable=print_context,
    )
