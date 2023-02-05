# from datetime import datetime, timedelta


# import airflow.DAG as DAG
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from ariflow import *

with DAG(
    "tutorial",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
) as dag:
    run_this = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    dummy = DummyOperator(
        task_id="dummy",
    )
