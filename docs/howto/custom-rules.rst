Custom Rules
============

Sometime, you need to add some custom rules to your migration. For example, you have some custom airflow operators
base on the existing ``PostgresOperator`` and you want to migrate them to dolphinscheduler. The custom operator
definition is like this:

.. code-block:: python

    # Just create a custom operator base on PostgresOperator, and do nothing except change the connection
    # arguments name from ``postgres_conn_id`` to ``my_custom_conn_id``
    from airflow.providers.postgres.operators.postgres import PostgresOperator

    class MyCustomOperator(PostgresOperator):
        def __init__(
            self,
            *,
            sql: str | Iterable[str],
            my_custom_conn_id: str = 'postgres_default',
            autocommit: bool = False,
            parameters: Iterable | Mapping | None = None,
            database: str | None = None,
            runtime_parameters: Mapping | None = None,
            **kwargs,
        ) -> None:
            super().__init__(
                sql=sql,
                postgres_conn_id=my_custom_conn_id,
                autocommit=autocommit,
                parameters=parameters,
                database=database,
                runtime_parameters=runtime_parameters,
                **kwargs,
            )

You put this operator same directory with your DAG file. and you airflow dags files are like this:

.. code-block:: text

    dags
     └── dag.py
    custom
     └── my_custom_operator.py

And in file ``dag.py``, you use this custom operator like this:

.. code-block:: python

    from custom.my_custom_operator import MyCustomOperator

    with DAG(
        dag_id='my_custom_dag',
        default_args=default_args,
        schedule_interval='@once',
        start_date=days_ago(2),
        tags=['example'],
    ) as dag:
        t1 = MyCustomOperator(
            task_id='my_custom_task',
            sql='select * from table',
            my_custom_conn_id='my_custom_conn_id',
        )


In this case, you can add a custom rule file named ``MyCustomOperator.yaml`` to tell airphin what you want to do
during the migration

.. code-block:: yaml

    name: MyCustomOperator
    description: The configuration for converting airflow custom operator MyCustomOperator to DolphinScheduler SQL task.
    
    migration:
      module:
        - action: replace
          src: custom.my_custom_operator.MyCustomOperator
          dest: pydolphinschsduler.tasks.sql.Sql
      parameter:
        - action: replace
          src: task_id
          dest: name
        - action: replace
          src: my_custom_conn_id
          dest: datasource_name

Save the yaml config file to any directory you want, and declare the path when you run the ``airphin`` command:

.. code-block:: bash

    airphin convert --rules /path/to/MyCustomOperator.yaml ~/airflow/dags/dag.py

And you can see the new DAG file directory ``~/airflow/dags`` named ``dag-airphin.py`` is created which is the
converted result of ``dag.py``.