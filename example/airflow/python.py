from pprint import pprint
from airflow.operators.python_operator import PythonOperator
from airflow import DAG
from datetime import datetime, timedelta


def print_context(ds, **kwargs):
    """Print the Airflow context and ds variable from the context."""
    pprint(kwargs)
    print(ds)
    return 'Whatever you return gets printed in the logs'


with DAG(
    'tutorial',
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:

    run_this = PythonOperator(
        task_id='print_the_context',
        python_callable=print_context,
    )

