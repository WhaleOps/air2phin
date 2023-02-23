Custom Rules
============

Create Custom Rule
------------------

Sometimes, you need to add some custom rules to your migration. For example, you have some custom airflow operators
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

You put this operator same directory as your DAG file. and your airflow dags files are like this:

.. code-block:: text

    dags
     └── dag.py
    custom
     └── my_custom_operator.py

And in the file ``dag.py``, you use this custom operator like this:

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


In this case, you can add a custom rule file named ``MyCustomOperator.yaml`` to tell air2phin what you want to do
during the migration

.. code-block:: yaml

    name: MyCustomOperator
    description: The configuration for migrating airflow custom operator MyCustomOperator to DolphinScheduler SQL task.
    
    migration:
      module:
        - action: replace
          src: custom.my_custom_operator.MyCustomOperator
          dest: pydolphinscheduler.tasks.sql.Sql
      parameter:
        - action: replace
          src: task_id
          dest: name
        - action: replace
          src: my_custom_conn_id
          dest: datasource_name

Use Custom Rule
---------------

Save the YAML config file to any directory you want, and declare the path when you run the ``air2phin`` command:

.. code-block:: bash

    air2phin migrate --custom-rules /path/to/MyCustomOperator.yaml ~/airflow/dags/dag.py

And you can see the new DAG file directory ``~/airflow/dags`` named ``dag-air2phin.py`` is created which is the
migrated result of ``dag.py``.

Use Multiple Custom Rules
-------------------------

Air2phin also supports using multiple custom rules in a single migration, and has directory and scatter files due
to different files organized.

In Single File and Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When all custom rules are in one single file or directory, use single options argument :code:`--custom-rules` or :code:`-r`
can use them

.. code-block:: bash

    # single file
    air2phin migrate --custom-rules /path/to/MyCustomOperator.yaml ~/airflow/dags/dag.py

    # single directory
    air2phin migrate --custom-rules /path/to/rules/dir ~/airflow/dags/dag.py

In Scatter Files or Directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, our rules will be in the different places, and air2phin support the use option argument :code:`--custom-rules` or :code:`-r`
multiple times in one single migration

.. code-block:: bash

    # multiple files
    air2phin migrate --custom-rules /path/to/MyCustomOperator1.yaml --custom-rules /path/to/MyCustomOperator2.yaml ~/airflow/dags/dag.py

    # multiple directories
    air2phin migrate --custom-rules /path/to/rules/dir1 --custom-rules /path/to/rules/dir2 ~/airflow/dags/dag.py

    # multiple mixed files and directories
    air2phin migrate --custom-rules /path/to/MyCustomOperator1.yaml --custom-rules /path/to/rules/dir1 ~/airflow/dags/dag.py

Use Custom Rule Only Without Built-ins
---------------------------------------

All the above examples using custom rules combine built-in rules and customs, sometimes we just want to apply
the custom rule to migrate existing files, just like we apply a patch to our codebase. We can use option argument
:code:`--custom-only` or :code:`-R` to use custom rules and ignore built-in.

.. code-block:: bash

    # Only use custom rules and ignore built-in one
    air2phin migrate --custom-rules /path/to/MyCustomOperator1.yaml --custom-only ~/airflow/dags/dag.py

It is useful when you have lots of files to migrate, if you found some code should change again after the first
migration run, but do not want to apply all the rules which cost lots of time, you can try to use this feature.

Use Rule Override
-----------------

Custom rules provide the ability to override built-in rules. Sometimes we want to override the built-in migrate
rules by custom one, we can use the same name as the built-in rule when you specify the custom rule.

For example, we have the build-in rule ``PythonOperator.yaml``, and the content as below:

.. code-block:: yaml

    name: PythonOperator
    description: The configuration for migrating Airflow PythonOperator to DolphinScheduler Python task.
    
    migration:
      module:
        - action: replace
          src:
            - airflow.operators.python_operator.PythonOperator
            - airflow.operators.python.PythonOperator
          dest: pydolphinscheduler.tasks.python.Python
      parameter:
        - action: replace
          src: task_id
          dest: name
        - action: replace
          src: python_callable
          dest: definition

If you want to run those python task base on the dolphinscheduler specific environment, the best practice is to use rule
override. Create a custom rule with the name ``CustomPythonOperator.yaml`` with content

.. code-block:: yaml

    name: PythonOperator
    description: The configuration for migrating Airflow PythonOperator to DolphinScheduler Python task.
    
    migration:
      module:
        - action: replace
          src:
            - airflow.operators.python_operator.PythonOperator
            - airflow.operators.python.PythonOperator
          dest: pydolphinscheduler.tasks.python.Python
      parameter:
        - action: replace
          src: task_id
          dest: name
        - action: replace
          src: python_callable
          dest: definition
        - action: add
          arg: environment_name
          default: 
            type: str
            value: airflow_migrate

We do nothing but add five new lines(Note that the ``name`` attribute in ``CustomPythonOperator.yaml`` is the
same as the value of built-in on in ``PythonOperator.yaml``)

.. code-block:: yaml

        - action: add
          arg: environment_name
          default: 
            type: str
            value: airflow_migrate

in ``CustomPythonOperator.yaml`` to tell air2phin add one new argument name ``environment_name`` with default
value ``airflow_migrate``, then we can use it by command

.. code-block:: bash

    air2phin migrate --custom-rules CustomPythonOperator.yaml ~/airflow/dags/dag.py

``PythonOperator.yaml`` will be overridden by ``CustomPythonOperator.yaml`` due to ``CustomPythonOperator.yaml``
have the same name and ``CustomPythonOperator.yaml`` is the custom rule.

.. note::

    We use the ``name`` attribute in the file content instead of the filename of identification
